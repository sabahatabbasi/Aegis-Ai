import json

def generate_report():
    try:
        # 1. Load the data
        with open("working_recon_output.json", "r") as f:
            data = json.loads(f.read())
        
        if isinstance(data, str): 
            data = json.loads(data)

        # 2. Build the table content
        report_lines = []
        divider = "=" * 125
        report_lines.append(divider)
        report_lines.append(f"MASTER RED TEAM PLAYBOOK: {data.get('target', 'Target Domain')}")
        report_lines.append(divider)
        
        header = f"| {'Phase':<15} | {'Task':<18} | {'Objective':<35} | {'Risk':<8} | {'Tool':<15} |"
        report_lines.append(header)
        report_lines.append("-" * 125)

        for phase in data.get('phases', []):
            p_name = phase.get('phase_name', 'General')
            for task in phase.get('tasks', []):
                t_name = task.get('task_name', 'N/A')
                obj = task.get('objective', 'N/A')
                risk = task.get('risk_level', 'Medium')
                tool = task.get('tool_suggested', 'Manual')
                
                row = f"| {p_name[:15]:<15} | {t_name[:18]:<18} | {obj[:35]:<35} | {risk:<8} | {tool:<15} |"
                report_lines.append(row)

        report_lines.append(divider)
        final_table = "\n".join(report_lines)

        # 3. Return the table (NOT print)
        return final_table

    except Exception as e:
        print(f"❌ Error: {e}")
        return ""
