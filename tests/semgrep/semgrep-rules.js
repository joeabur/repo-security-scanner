const child_process = require("child_process");
const crypto = require("crypto");
const https = require("https");
const { exec, execSync } = require("child_process");

function evaluate(x) {
  // ruleid: reposcan.js.eval-call
  eval(x);
  // ok: reposcan.js.eval-call
  eval("1 + 1");
}

function compile(src) {
  // ruleid: reposcan.js.new-function
  return new Function(src);
  // ok: reposcan.js.new-function
  return new Function("return 1");
}

function run(host, name) {
  // ruleid: reposcan.js.child-process-command-injection
  child_process.exec("ping " + host);
  // ruleid: reposcan.js.child-process-command-injection
  child_process.execSync(`ls ${name}`);
  // ruleid: reposcan.js.child-process-command-injection
  exec("ls " + name);
  // ruleid: reposcan.js.child-process-command-injection
  execSync(`cat ${name}`);
  // ok: reposcan.js.child-process-command-injection
  child_process.execFile("ping", [host]);
  // ok: reposcan.js.child-process-command-injection
  exec("ls -l");
  // ok: reposcan.js.child-process-command-injection
  /a+/.exec("aaa" + name);
}

function render(el, html, text) {
  // ruleid: reposcan.js.html-injection-sink
  el.innerHTML = html;
  // ruleid: reposcan.js.html-injection-sink
  el.outerHTML = html;
  // ruleid: reposcan.js.html-injection-sink
  document.write(html);
  // ok: reposcan.js.html-injection-sink
  el.innerHTML = "<b>static</b>";
  // ok: reposcan.js.html-injection-sink
  el.textContent = text;
}

function tls() {
  // ruleid: reposcan.js.tls-verification-disabled
  https.request({ host: "x", rejectUnauthorized: false });
  // ruleid: reposcan.js.tls-verification-disabled
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  // ok: reposcan.js.tls-verification-disabled
  https.request({ host: "x", rejectUnauthorized: true });
}

function hash(data) {
  // ruleid: reposcan.js.weak-hash
  crypto.createHash("md5").update(data);
  // ruleid: reposcan.js.weak-hash
  crypto.createHash("sha1").update(data);
  // ok: reposcan.js.weak-hash
  crypto.createHash("sha256").update(data);
}
