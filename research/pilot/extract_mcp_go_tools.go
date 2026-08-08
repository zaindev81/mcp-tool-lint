// Command extract_mcp_go_tools extracts the subset of mcp-go NewTool calls
// needed by this pilot. It intentionally supports only literal/constant names,
// descriptions, and the four annotation option functions.
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strconv"
)

type extractedTool struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Annotations map[string]bool `json:"annotations"`
	Source      string          `json:"_source"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: go run extract_mcp_go_tools.go SOURCE.go")
		os.Exit(2)
	}

	filename := os.Args[len(os.Args)-1]
	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, filename, nil, 0)
	if err != nil {
		panic(err)
	}

	constants := map[string]string{}
	for _, declaration := range file.Decls {
		general, ok := declaration.(*ast.GenDecl)
		if !ok || general.Tok != token.CONST {
			continue
		}
		for _, specification := range general.Specs {
			values := specification.(*ast.ValueSpec)
			for index, name := range values.Names {
				if index < len(values.Values) {
					if value, ok := stringValue(values.Values[index], constants); ok {
						constants[name.Name] = value
					}
				}
			}
		}
	}

	var tools []extractedTool
	ast.Inspect(file, func(node ast.Node) bool {
		call, ok := node.(*ast.CallExpr)
		if !ok || selectorName(call.Fun) != "NewTool" || len(call.Args) == 0 {
			return true
		}
		name, ok := stringValue(call.Args[0], constants)
		if !ok {
			return true
		}

		tool := extractedTool{
			Name:        name,
			Annotations: map[string]bool{},
			Source:      fmt.Sprintf("%s:%d", filepath.ToSlash(filename), fset.Position(call.Pos()).Line),
		}
		for _, argument := range call.Args[1:] {
			option, ok := argument.(*ast.CallExpr)
			if !ok || len(option.Args) == 0 {
				continue
			}
			switch selectorName(option.Fun) {
			case "WithDescription":
				tool.Description, _ = stringValue(option.Args[0], constants)
			case "WithReadOnlyHintAnnotation":
				tool.Annotations["readOnlyHint"], _ = boolValue(option.Args[0])
			case "WithDestructiveHintAnnotation":
				tool.Annotations["destructiveHint"], _ = boolValue(option.Args[0])
			case "WithIdempotentHintAnnotation":
				tool.Annotations["idempotentHint"], _ = boolValue(option.Args[0])
			case "WithOpenWorldHintAnnotation":
				tool.Annotations["openWorldHint"], _ = boolValue(option.Args[0])
			}
		}
		tools = append(tools, tool)
		return true
	})

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(tools); err != nil {
		panic(err)
	}
}

func selectorName(expression ast.Expr) string {
	switch value := expression.(type) {
	case *ast.SelectorExpr:
		return value.Sel.Name
	case *ast.Ident:
		return value.Name
	default:
		return ""
	}
}

func stringValue(expression ast.Expr, constants map[string]string) (string, bool) {
	switch value := expression.(type) {
	case *ast.BasicLit:
		if value.Kind != token.STRING {
			return "", false
		}
		decoded, err := strconv.Unquote(value.Value)
		return decoded, err == nil
	case *ast.Ident:
		result, ok := constants[value.Name]
		return result, ok
	case *ast.ParenExpr:
		return stringValue(value.X, constants)
	case *ast.BinaryExpr:
		if value.Op != token.ADD {
			return "", false
		}
		left, leftOK := stringValue(value.X, constants)
		right, rightOK := stringValue(value.Y, constants)
		return left + right, leftOK && rightOK
	default:
		return "", false
	}
}

func boolValue(expression ast.Expr) (bool, bool) {
	identifier, ok := expression.(*ast.Ident)
	if !ok {
		return false, false
	}
	switch identifier.Name {
	case "true":
		return true, true
	case "false":
		return false, true
	default:
		return false, false
	}
}
