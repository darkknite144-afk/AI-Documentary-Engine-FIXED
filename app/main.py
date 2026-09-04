import argparse
from app.pipeline.orchestrator import orchestrator
from app.storage.json_store import project_store
from app.utils.logging import setup_logger

logger = setup_logger("main")

def main():
    parser = argparse.ArgumentParser(description="AI Documentary Story Engine CLI")
    parser.add_argument("command", choices=["generate", "status", "export"], help="Command to run")
    parser.add_argument("--topic", type=str, help="Topic for the documentary (for 'generate')")
    parser.add_argument("--duration", type=int, default=5, help="Target duration in minutes")
    parser.add_argument("--language", type=str, default="Hinglish", help="Target language (e.g. Hinglish, English, Hindi)")
    parser.add_argument("--project_id", type=str, help="Project ID (for 'status' or 'export')")

    args = parser.parse_args()

    if args.command == "generate":
        if not args.topic:
            print("Error: --topic is required for generate command.")
            return
            
        print(f"\n[🚀] Starting AI Documentary Engine for: '{args.topic}'")
        print(f"[*] Duration: {args.duration} mins | Language: {args.language}")
        print("[*] Please wait, this will take a few minutes as multiple AI agents work...\n")
        
        try:
            project_id = orchestrator.run_pipeline(args.topic, args.duration, args.language)
            print(f"\n[✅] SUCCESS! Project created with ID: {project_id}")
            print(f"To see status: python -m app.main status --project_id {project_id}")
            print(f"To export markdown script: python -m app.main export --project_id {project_id}")
        except Exception as e:
            print(f"\n[❌] Pipeline failed: {str(e)}")

    elif args.command == "status":
        if not args.project_id:
            print("Error: --project_id is required for status command.")
            return
            
        project = project_store.load_project(args.project_id)
        if project:
            print(f"\nProject Topic: {project.topic}")
            print(f"Current Status: {project.status}")
            print(f"Quality Gate: {project.quality_gate_status}")
            print(f"Generated Drafts: {len(project.drafts)}")
        else:
            print("Project not found.")

    elif args.command == "export":
        if not args.project_id:
            print("Error: --project_id is required for export command.")
            return
            
        project = project_store.load_project(args.project_id)
        if project and project.status in ["COMPLETED", "NEEDS_REVIEW"]:
            export_path = f"{project.project_id}_script.md"
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(f"# TITLE: {project.angle.get('title', project.topic)}\n\n")
                f.write(f"**Target Duration:** {args.duration} mins\n")
                f.write(f"**Quality Gate:** {project.quality_gate_status}\n\n")
                f.write("---\n\n")
                
                for section in project.master_script.get("sections", []):
                    f.write(f"## {section.get('title')}\n")
                    f.write(f"> **VISUAL:** *{section.get('visual_idea')}*\n\n")
                    f.write(f"**NARRATION:**\n{section.get('narration')}\n\n")
                    f.write("---\n")
            print(f"\n[✅] Script exported successfully to {export_path}")
        else:
            print("Project not found or pipeline not completed yet.")

if __name__ == "__main__":
    main()
