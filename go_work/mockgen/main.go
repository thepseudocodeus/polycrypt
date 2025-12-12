/*
 * Mockgen creates a data directory of files to test encryption and decryption code
 */
package main

import (
	"encoding/csv"
	"fmt"
	"image/jpeg"
	"image/png"
	"os"
	"path/filepath"
	"time"

	"github.com/brianvoe/gofakeit/v7"
	//"github.com/brianvoe/gofakeit/v7/source"
	//"math/rand/v2"
)

// [] TODO: move this to a yaml file
type Config struct {
	BaseDir    string // directory created to test encryption
	TextFiles  int
	CsvFiles   int
	ImageFiles int
	SubDirs    int
}

func main() {
	// [] TODO: Can I ensure proper placement at root somehow?
	// Notes:
	// - could invert recursively walk from this file up looking for:
	// 	- Taskfile.yml or Taskfile.yaml = True
	// 	- pyproject.toml = True
	// - probability of both conditions being true in first place discovered and not the project root conjectured to be <= 3% which is acceptable for now
	// - assumes all projects use uv and task-go which is currently true but how to deal with if development preferences change?
	// - perhaps add root project name as well
	// - Hypothesis:
	// 	- instead of this make this mathematic
	// 	- possible states of root:
	// 		- *_work directories exist = True
	// 			- 5 points per each
	// 		- Taskfile exists without extension consideration in case it changes = True
	// 			- 10 points
	// 		- pyproject exists without extension = True
	// 			- 10 points
	// 		- .yml exists = True
	// 			- 1 point per
	// 		- .yaml exists = True
	// 			- 1 point per
	// 		- .toml exists = True
	// 			- 2 points per
	// 		- .env exists = True
	// 			- 20 points
	// 		- .git dir exists = True
	// 			- 10 points
	// 		- .gitignore exists = True
	// 			- 20 points
	// 	- start with guess that >=50 points = is root = True
	// 	- write julia program that checks this assumption on private apps and updates scoring:
	// 		- 10 apps in home AI Lab
	// 		- 20 apps in quantitative trading engine
	// 		- 100 client created apps
	// 		- 30 git repos @github.com/dataninja-python and @github.com/thepseudocodeus
	// 	- use beysian updating to adjust likely flawed initial point amount
	// [] TODO: this is really long move to markdown
	config := Config{
		BaseDir:    "../../mock_data", // Assumes project has a go_work/go workspace/this app is here
		TextFiles:  5,
		CsvFiles:   2,
		ImageFiles: 3,
		SubDirs:    2,
	}

	fmt.Printf("--- Generating Mock Data in '%s' ---\n", config.BaseDir)
	if err := generateMockData(config); err != nil {
		fmt.Printf("FATAL Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("--- Generation Complete. Ready for TDD. ---")
}

func generateMockData(cfg Config) error {
	// Create the directory
	// Note: ensure this happens first
	// Note: had to add removal first to prevent error
	if err := os.RemoveAll(cfg.BaseDir); err != nil {
		return err
	}
	if err := os.MkdirAll(cfg.BaseDir, 0755); err != nil {
		return err
	}

	// Add files to directory
	for i := 0; i < cfg.TextFiles; i++ {
		writeTextFile(filepath.Join(cfg.BaseDir, fmt.Sprintf("document_%d.txt", i)), gofakeit.Paragraph(5, 10, 50, " "))
	}
	for i := 0; i < cfg.CsvFiles; i++ {
		writeCSVFile(filepath.Join(cfg.BaseDir, fmt.Sprintf("transactions_%d.csv", i)), 100)
	}
	for i := 0; i < cfg.ImageFiles; i++ {
		writeImageFile(filepath.Join(cfg.BaseDir, fmt.Sprintf("photo_%d.jpg", i)), 640, 480)
	}

	// Note: subdirectories are handled here
	// Leave in this note because couldn't find implementation in an older app
	for i := 0; i < cfg.SubDirs; i++ {
		subDir := filepath.Join(cfg.BaseDir, fmt.Sprintf("internal_data_%d", i))
		if err := os.MkdirAll(subDir, 0755); err != nil {
			return err
		}
		writeTextFile(filepath.Join(subDir, "secret_note.md"), gofakeit.HackerPhrase())
		writeImageFile(filepath.Join(subDir, "thumb.png"), 100, 100) // prefer png change if not useful
	}

	return nil
}

// writeTextFile creates text file
func writeTextFile(path string, content string) {
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Printf("Error writing text file %s: %v\n", path, err)
	}
}

// writeCSVFile creates mock csv file
func writeCSVFile(path string, rows int) {
	file, err := os.Create(path)
	if err != nil {
		fmt.Printf("Error creating CSV file %s: %v\n", path, err)
		return
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Generate header
	writer.Write([]string{"UserID", "Timestamp", "Amount", "Description"})

	// Generate rows
	// Old: for i := 0; i < rows; i++ {
	for range rows {
		record := []string{
			gofakeit.UUID(),
			gofakeit.DateRange(time.Now().AddDate(0, -6, 0), time.Now()).Format("2006-01-02"),
			fmt.Sprintf("%.2f", gofakeit.Float64Range(1.0, 1000.0)),
			gofakeit.HackerPhrase(),
		}
		writer.Write(record)
	}
}

// Separate functionality for creating jpeg
func writeImageFile(path string, width, height int) {
	// Make image
	// [] TODO: confirm image type (RGBA? or other)
	img := gofakeit.Image(width, height)

	file, err := os.Create(path)
	if err != nil {
		fmt.Printf("Error creating image file %s: %v\n", path, err)
		return
	}
	defer file.Close()

	if filepath.Ext(path) == ".png" {
		png.Encode(file, img)
	} else {
		// [] TODO: make it able to be multiple types
		jpeg.Encode(file, img, nil)
	}
}
