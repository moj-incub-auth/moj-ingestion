python parse_component_to_json.py alert-combined.md -o alert-component.json --pretty

 Let me also show you just the component metadata (without the full file content) for easier viewing:                                                                   
                                                                                                                                                                                                                 
● Bash(python -c "import json; data = json.load(open('alert-component.json')); del data['filecontent']; print(json.dumps(data, indent=2))")                                                                      
  ⎿  Running…                                                                                                                                                                                                    
                                                                                                                                                                                                                 
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Bash command                                                                                                                                                                                                    
                                                                                                                                                                                                                 
   python -c "import json; data = json.load(open('alert-component.json')); del data['filecontent']; print(json.dumps(data, indent=2))"                                                                           
   Display component metadata without full file content