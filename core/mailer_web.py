import subprocess

def copy_email_to_clipboard(html_text):
    # Wrap in basic HTML structure
    full_html = f"<html><body>{html_text}</body></html>"
    
    # We use xclip to set the selection to 'clipboard' 
    # and the target type to 'text/html'
    try:
        process = subprocess.Popen(
            ['xclip', '-selection', 'clipboard', '-t', 'text/html'],
            stdin=subprocess.PIPE
        )
        process.communicate(input=full_html.encode('utf-8'))
        print("HTML copied to clipboard successfully!")
    except FileNotFoundError:
        print("Error: 'xclip' is not installed. Run 'sudo apt install xclip'.")

# Example usage:
# copy_email_to_clipboard("<h1>Hello!</h1><p>This is <b>bold</b> text.</p>")