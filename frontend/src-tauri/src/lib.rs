use std::process::{Command, Stdio, ChildStdin, ChildStdout};
use std::io::{BufRead, BufReader, Write};
use std::sync::Mutex;
use tauri::{State, AppHandle};
use tauri_plugin_shell::ShellExt;

struct PythonProcess {
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

struct AppState {
    process: Mutex<Option<PythonProcess>>,
}

#[tauri::command]
fn python_ipc(payload: String, state: State<'_, AppState>, app: AppHandle) -> Result<String, String> {
    let mut proc_guard = state.process.lock().unwrap();

    if proc_guard.is_none() {
        use tauri::Manager;
        let resource_dir = app.path().resource_dir().map_err(|e| e.to_string())?;
        let exe_name = if cfg!(target_os = "windows") {
            "ipc_bridge.exe"
        } else {
            "ipc_bridge"
        };
        let sidecar_path = resource_dir
            .join("resources")
            .join("ipc_bridge_app")
            .join(exe_name);
        
        let mut child = Command::new(sidecar_path);
        
        child.stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit());
        
        let mut child = child.spawn()
            .map_err(|e| format!("Failed to spawn Python bridge: {}", e))?;

        let stdin = child.stdin.take().ok_or("Failed to open stdin")?;
        let stdout = BufReader::new(child.stdout.take().ok_or("Failed to open stdout")?);

        *proc_guard = Some(PythonProcess { stdin, stdout });
    }

    let process = proc_guard.as_mut().unwrap();

    writeln!(process.stdin, "{}", payload).map_err(|e| format!("Failed to write to stdin: {}", e))?;
    process.stdin.flush().map_err(|e| format!("Failed to flush stdin: {}", e))?;

    let mut line = String::new();
    process.stdout.read_line(&mut line).map_err(|e| format!("Failed to read line: {}", e))?;

    let trimmed = line.trim();
    if trimmed.starts_with('{') || trimmed.starts_with('[') {
        return Ok(trimmed.to_string());
    }

    Err(format!("No valid JSON output received: {}", trimmed))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState {
            process: Mutex::new(None),
        })
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![python_ipc])
        .on_window_event(|_window, event| match event {
            tauri::WindowEvent::CloseRequested { .. } => {
                std::process::exit(0);
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
