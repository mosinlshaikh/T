package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

type apiResponse struct {
	Success bool            `json:"success"`
	Message string          `json:"message"`
	Data    json.RawMessage `json:"data"`
}

func main() {
	baseURL := strings.TrimRight(os.Getenv("TTRL_BACKEND_URL"), "/")
	if baseURL == "" {
		baseURL = "http://127.0.0.1:8000"
	}

	client := http.Client{Timeout: 10 * time.Second}
	response, err := client.Get(baseURL + "/monitor/paper-live")
	if err != nil {
		fmt.Printf("market_probe_status=backend_unavailable error=%T\n", err)
		os.Exit(1)
	}
	defer response.Body.Close()

	body, err := io.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("market_probe_status=read_failed error=%T\n", err)
		os.Exit(1)
	}

	var parsed apiResponse
	if err := json.Unmarshal(body, &parsed); err != nil {
		fmt.Printf("market_probe_status=invalid_json status_code=%d\n", response.StatusCode)
		os.Exit(1)
	}

	fmt.Printf(
		"market_probe_status=ok http_status=%d success=%v message=%q bytes=%d\n",
		response.StatusCode,
		parsed.Success,
		parsed.Message,
		len(body),
	)
}
