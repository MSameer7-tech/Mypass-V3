use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader, Write};

#[tauri::command]
fn python_ipc(payload: String) -> Result<String, String> {
    let python_bin = "/Users/sameer/Documents/Password-Manager-App/.venv/bin/python";
    let script_path = "/Users/sameer/Documents/Password-Manager-App/backend/ipc_bridge.py";

    let mut child = Command::new(python_bin)
        .arg(script_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python bridge: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        writeln!(stdin, "{}", payload).map_err(|e| format!("Failed to write to stdin: {}", e))?;
    }

    let stdout = child.stdout.take().ok_or("Failed to open stdout")?;
    let reader = BufReader::new(stdout);

    for line_result in reader.lines() {
        let line = line_result.map_err(|e| format!("Failed to read line: {}", e))?;
        let trimmed = line.trim();
        if trimmed.starts_with('{') || trimmed.starts_with('[') {
            return Ok(trimmed.to_string());
        }
    }

    Err("No valid JSON output received from Python backend process.".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![python_ipc])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
