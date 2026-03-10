python parse_component_to_json.py alert-combined.md -o alert-component.json --pretty

 Let me also show you just the component metadata (without the full file content) for easier viewing:                                                                   
                                                                                                                                                                                                                 
● Bash(python -c "import json; data = json.load(open('alert-component.json')); del data['filecontent']; print(json.dumps(data, indent=2))")                                                                      
  ⎿  Running…                                                                                                                                                                                                    
                                                                                                                                                                                                                 
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Bash command                                                                                                                                                                                                    
                                                                                                                                                                                                                 
   python -c "import json; data = json.load(open('alert-component.json')); del data['filecontent']; print(json.dumps(data, indent=2))"                                                                           
   Display component metadata without full file content

    Bash(python -c "import json; data = json.load(open('alert-component.json')); del data['filecontent']; print(json.dumps(data, indent=2))")                                                                      
  ⎿  {                                                                                                                                                                                                           
       "components": [                                                                                                                                                                                           
         {                                                                                                                                                                                                       
     … +40 lines (ctrl+o to expand)                                                                                                                                                                              
                                                                                                                                                                                                                 
● Perfect! I've successfully parsed the alert-combined.md file and created a structured JSON output. Here's what was extracted:                                                                                  
                                                       
  ✅ Successfully Extracted:                                                                                                                                                                                     
                                                                                                                                                                                                                 
  - Title: "Alert"                                                                                                                                                                                               
  - URL: Generated based on the component path                                                                                                                                                                   
  - Description: "The alert component presents 1 of 4 types of alerts to a user..."                                                                                                                              
  - Parent: "MOJ Design System" (detected from file paths)                                                                                                                                                       
  - Accessibility: "AA" (default for government services)                                                                                                                                                        
  - Dates: Current timestamp (can be customized)                                                                                                                                                                 
  - Has Research: true (detected "Examples" section)                                                                                                                                                             
  - Views: 0 (default, typically tracked separately)
  - Sections: All 6 source files listed with their paths
  - File Content: The complete markdown content is preserved in filecontent

  📄 Files Created:

  1. parse_component_to_json.py - The parser script
  2. alert-component.json - The generated JSON output

  🚀 Usage:

  # Basic usage
  python parse_component_to_json.py alert-combined.md -o alert-component.json --pretty

  # Or output to stdout
  python parse_component_to_json.py alert-combined.md --pretty

  # Process other component files
  python parse_component_to_json.py button-combined.md -o button-component.json --pretty

  The script automatically:
  - Extracts frontmatter metadata
  - Identifies the main component title
  - Generates appropriate URLs
  - Detects if research/examples are included
  - Preserves all source file information
  - Keeps the complete file content for reference
