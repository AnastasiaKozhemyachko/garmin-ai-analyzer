const fs = require("fs");
const path = require("path");
const { exec, execSync } = require("child_process");

// Configuration
const CONFIG = {
  filePath: path.resolve(process.argv[2] || "./results/all_data.json"),
  chatUrl: "https://chatgpt.com/",
  delayMs: 3000,
  finderWaitMs: 2000,
  uploadWaitMs: 20000,
  prompt: `Проанализируй данные из файла.

Сделай:
1) короткий итог (3–5 строк)
2) что настораживает (HRV/RHR/сон/стресс — если есть)
3) вероятность, что я начинаю заболевать (низкая/средняя/высокая) + почему
4) план на ближайшие 3 дня.`,
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const runAppleScript = (script) =>
  new Promise((resolve, reject) => {
    const cmd = `osascript -e '${script.replace(/'/g, "'\\\\''")}'`;
    exec(cmd, (err, stdout, stderr) => {
      if (err) return reject(err);
      resolve({ stdout, stderr });
    });
  });

const selectAndCopyFile = (filePath) =>
  runAppleScript(`
tell application "Finder"
  activate
  select file (POSIX file "${filePath}" as alias)
  delay 1
end tell

tell application "System Events"
  keystroke "c" using {command down}
  delay 1
end tell
`);

const openChatGPT = (url) =>
  runAppleScript(`
tell application "Google Chrome"
  activate
  open location "${url}"
end tell
delay 3
`);

const pasteFile = () =>
  runAppleScript(`
tell application "Google Chrome"
  activate
  delay 1
end tell

tell application "System Events"
  keystroke "v" using {command down}
  delay 2
end tell
`);

const sendPrompt = (prompt) => {
  execSync("pbcopy", { input: prompt });
  return runAppleScript(`
tell application "System Events"
  keystroke "v" using {command down}
  delay 1
  key code 36
end tell
`);
};

(async () => {
  if (!fs.existsSync(CONFIG.filePath)) {
    console.error(`❌ File not found: ${CONFIG.filePath}`);
    process.exit(1);
  }

  const absolutePath = path.resolve(CONFIG.filePath);
  console.log(`✅ File: ${absolutePath}`);

  console.log("📂 Opening file in Finder...");
  execSync(`open -R "${absolutePath}"`);
  await sleep(CONFIG.finderWaitMs);

  console.log("📋 Selecting and copying file...");
  await selectAndCopyFile(absolutePath);

  console.log("🌐 Opening ChatGPT...");
  await openChatGPT(CONFIG.chatUrl);
  await sleep(CONFIG.delayMs);

  console.log("📎 Pasting file...");
  await pasteFile();
  await sleep(CONFIG.uploadWaitMs);

  console.log("📝 Sending prompt...");
  await sendPrompt(CONFIG.prompt);

  console.log("✅ Done");
})().catch((e) => {
  console.error("❌ Error:", e);
  process.exit(1);
});
