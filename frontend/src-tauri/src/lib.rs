use std::process::{Command, Stdio, ChildStdin, ChildStdout};
use std::io::{BufRead, BufReader, Write};
use std::sync::Mutex;
use tauri::State;

struct PythonProcess {
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

struct AppState {
    process: Mutex<Option<PythonProcess>>,
}

#[tauri::command]
fn python_ipc(payload: String, state: State<'_, AppState>) -> Result<String, String> {
    let mut proc_guard = state.process.lock().unwrap();

    if proc_guard.is_none() {
        let python_bin = "/Users/sameer/Documents/Password-Manager-App/.venv/bin/python";
        let script_path = "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py";

        let mut child = Command::new(python_bin)
            .arg(script_path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|e| format!("Failed to spawn Python bridge: {}", e))?;

        let stdin = child.stdin.take().ok_or("Failed to open stdin")?;
        let stdout = BufReader::new(child.stdout.take().ok_or("Failed to open stdout")?);

        *proc_guard = Some(PythonProcess { stdin, stdout });
    }

    let process = proc_guard.as_mut().unwrap();

    writeln!(process.stdin, "{}", payload).map_err(|e| format!("Failed to write to stdin: {}", e))?;

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
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![python_ipc])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
