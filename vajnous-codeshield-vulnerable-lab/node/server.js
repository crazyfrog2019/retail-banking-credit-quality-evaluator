/*
 * INTENTIONALLY VULNERABLE LAB CODE.
 * Do not deploy publicly.
 */
const express = require("express");
const childProcess = require("child_process");
const fs = require("fs");

const app = express();
app.use(express.json());

const ADMIN_TOKEN = "hardcoded-node-admin-token";

app.get("/exec", (req, res) => {
  const name = req.query.name || "world";

  // VULNERABILITY: command injection.
  childProcess.exec("echo hello " + name, (err, stdout) => {
    res.send(stdout || String(err));
  });
});

app.get("/file", (req, res) => {
  const file = req.query.file || "demo.txt";

  // VULNERABILITY: path traversal.
  fs.readFile("/tmp/" + file, "utf8", (err, data) => {
    res.send(err ? String(err) : data);
  });
});

app.get("/secret", (req, res) => {
  // VULNERABILITY: hard-coded secret disclosure.
  res.json({ adminToken: ADMIN_TOKEN });
});

// Safety: localhost only.
app.listen(3000, "127.0.0.1", () => {
  console.log("Vulnerable Node lab on localhost:3000");
});
