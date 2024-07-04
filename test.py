#IMPORT REQUIRED PACKAGES
import argparse, os, sys, random, string, webbrowser
import google.generativeai as genai
#tqdm adds progress bars
from tqdm import tqdm

#OpenAI token for accessing chatGPT
genai.configure(api_key='AIzaSyCfVmgpZngK_-si-ls09dM0IdMy2dSBYt0')

model = genai.GenerativeModel(
    model_name = "gemini-1.5-flash",
    system_instruction = "Give Code review of the given code changes."
)

def add_code_tags(text):
    import re

    matches = re.finditer(r"`.+?`", text)

    updated_chunks = []
    last_end = 0

    for match in matches:
        updated_chunks.append(text[last_end : match.start()])
        updated_chunks.append("<b>`{}`</b>".format(match.group(1)))
        last_end = match.end()
    
    return "".join(updated_chunks)

def generate_comment(diff, chatbot_context):
    chatbot_context.append(
        {
            "parts" : f"Give code review for the following changes: {diff}",
            "text": "none",
            "mime_type": "none",
            "data": f"{diff}"
        }
    )

    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(
                chatbot_context
            )
        
        except Exception as e:
            if attempt == retries - 1:
                print(f"attempt: {attempt}, retries: {retries}")
                raise e
            else:
                print("Error occured. Retrying....")
    
    comment = response.text

    chatbot_context = [
        {
            "content" : f"Give code review for then following changes: {diff}",
        },
        # {
        #     "content" : comment
        # },
    ]

    return comment, chatbot_context

def create_html_output(title, description, changes, prompt):
    random_string = "".join(random.choices(string.ascii_letters, k=5))
    output_file_name = random_string + "-output.html"

    title_text = f"\nTitle: {title}" if title else ""
    description_text = f"\nDescription: {description}" if description else ""
    chatbot_context = [
       {
             "content": f"{prompt}{title_text}{description_text}",
       }
    ]

    html_output = "<html>\n<head>\n<style>\n"
    html_output += "body {\n    font-family: Roboto, Ubuntu, Cantarell, Helvetica Neue, sans-serif;\n    margin: 0;\n    padding: 0;\n}\n"
    html_output += "pre {\n    white-space: pre-wrap;\n    background-color: #f6f8fa;\n    border-radius: 3px;\n    font-size: 85%;\n    line-height: 1.45;\n    overflow: auto;\n    padding: 16px;\n}\n"
    html_output += "</style>\n"
    html_output += '<link rel="stylesheet"\n href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">\n <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>\n'
    html_output += "<script>hljs.highlightAll();</script>\n"
    html_output += "</head>\n<body>\n"
    html_output += "<div style='background-color: #333; color: #fff; padding: 20px;'>"
    html_output += "<h1 style='margin: 0;'>AI code review</h1>"
    html_output += f"<h3>Diff to review: {title}</h3>" if title else ""
    html_output += "</div>"

    with tqdm(total=len(changes), desc="Making code review", unit="diff") as pbar:
       for i, change in enumerate(changes):
             diff = change["diff"]
             comment, chatbot_context = generate_comment(diff, chatbot_context)
             pbar.update(1)
             # Write the diff and comment to the HTML
             html_output += f"<h3>Diff</h3>\n<pre><code>{diff}</code></pre>\n"
             html_output += f"<h3>Comment</h3>\n<pre>{add_code_tags(comment)}</pre>\n"
    html_output += "</body>\n</html>"

    with open(output_file_name, "w") as f:
       f.write(html_output)

    return output_file_name

def get_diff_changes_from_pipeline():
    piped_input = sys.stdin.read()
    diffs = piped_input.split("diff --git")
    diff_list = [{"diff": diff} for diff in diffs if diff]
    return diff_list

def main():
    title, description, prompt = None, None, None
    changes = [{"diff":"""
    diff --git a/default/views.py b/default/views.py
    index 57786800..6e0e97ae 100644
    --- a/default/views.py
    +++ b/default/views.py
    @@ -2912,19 +2912,18 @@ class SystemHealthCheck(APIView):
                ssh_client.close()
                data = {
                    'hostname': hostname,
    -                'ram_used_gb':ram_used_gb,
    +                'ram_used_in_gb':ram_used_gb,
                    'ram_utilization': ram_utilization,
    -                'allocated_ram_gb':allocated_ram_gb,
    +                'ram_allocated_in_gb':allocated_ram_gb,
                    'cpu_utilization': cpu_utilization,
                    'cpu_allocated':cpu_allocated_percentage,
                    'cpu_freq': cpu_freq,
                    'total_memory': allocated_ram_bytes,
                    'cores': cores,
                    'threads': threads,
    -                'total_disk_storage_gb': total_disk_storage_gb,
    -                'used_disk_space_gb':used_disk_space_gb,
    -                'free_disk_space_gb':free_disk_space_gb
    -
    +                'total_disk_storage_in_gb': total_disk_storage_gb,
    +                'used_disk_space_in_gb':used_disk_space_gb,
    +                'free_disk_space_in_gb':free_disk_space_gb
                }
                return data
    @@ -2959,18 +2958,18 @@ class SystemHealthCheck(APIView):
            cpu_allocated_percentage = round(cpu_utilization / cores, 2)
            data = {
                    'hostname': hostname,
    -                'ram_used_gb':ram_used_gb,
    +                'ram_used_in_gb':ram_used_gb,
                    'ram_utilization': ram_utilization,
    -                'allocated_ram_gb':allocated_ram_gb,
    +                'ram_allocated_in_gb':allocated_ram_gb,
                    'cpu_utilization': cpu_utilization,
                    'cpu_allocated':cpu_allocated_percentage,
                    'cpu_freq': cpu_freq,
                    'total_memory': allocated_ram_bytes,
                    'cores': cores,
                    'threads': threads,
    -                'total_disk_storage_gb': total_disk_storage_gb,
    -                'used_disk_space_gb':used_disk_space_gb,
    -                'free_disk_space_gb':free_disk_space_gb
    +                'total_disk_storage_in_gb': total_disk_storage_gb,
    +                'used_disk_space_in_gb':used_disk_space_gb,
    +                'free_disk_space_in_gb':free_disk_space_gb
                }
            return data
    \ No newline at end of file
    """}]
    parser = argparse.ArgumentParser(description="AI code review script")
    parser.add_argument("--title", type=str, help="Title of the diff")
    parser.add_argument("--description", type=str, help="Description of the diff")
    # parser.add_argument("--prompt", type=str, help="Custom prompt for the AI")
    args = parser.parse_args()
    title = args.title if args.title else title
    description = args.description if args.description else description
    # prompt = args.prompt if args.prompt else PROMPT_TEMPLATE
    output_file = create_html_output(title, description, changes,"Custom prompt for the AI")#, prompt)
    try:
       webbrowser.open(output_file)
    except Exception:
       print(f"Error running the web browser, you can try to open the outputfile: {output_file} manually")

if __name__ == "__main__":
    main()
