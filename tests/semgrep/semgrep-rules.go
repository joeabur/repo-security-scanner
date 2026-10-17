package main

import (
	"crypto/md5"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/tls"
	"database/sql"
	"fmt"
	"os/exec"
)

func tlsConfig() {
	// ruleid: reposcan.go.insecure-skip-verify
	_ = &tls.Config{InsecureSkipVerify: true}
	// ok: reposcan.go.insecure-skip-verify
	_ = &tls.Config{InsecureSkipVerify: false}
	// ok: reposcan.go.insecure-skip-verify
	_ = &tls.Config{MinVersion: tls.VersionTLS12}
}

func shell(cmd string) {
	// ruleid: reposcan.go.exec-shell-command
	exec.Command("sh", "-c", cmd)
	// ruleid: reposcan.go.exec-shell-command
	exec.Command("/bin/bash", "-c", "echo "+cmd)
	// ok: reposcan.go.exec-shell-command
	exec.Command("sh", "-c", "echo hello")
	// ok: reposcan.go.exec-shell-command
	exec.Command("ls", "-l", cmd)
}

func digests(b []byte) {
	// ruleid: reposcan.go.weak-hash
	_ = md5.Sum(b)
	// ruleid: reposcan.go.weak-hash
	_ = sha1.New()
	// ok: reposcan.go.weak-hash
	_ = sha256.Sum256(b)
}

func queries(db *sql.DB, name string) {
	// ruleid: reposcan.go.sql-string-building
	db.Query("SELECT * FROM t WHERE n = '" + name + "'")
	// ruleid: reposcan.go.sql-string-building
	db.Exec(fmt.Sprintf("DELETE FROM t WHERE n = '%s'", name))
	// ok: reposcan.go.sql-string-building
	db.Query("SELECT * FROM t WHERE n = ?", name)
}
