import google.generativeai as genai
from google.cloud import bigquery, speech
from google.oauth2 import service_account
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




# Replace with your actual bot token
BOT_TOKEN = "7974533848:AAGH03VguQ_ue_3x2c0GpJHeaKGOJPD7AJk"

# Email credentials
sender_email = "bishnuhaldar560@gmail.com"
sender_password = "bdtxctzvslnfadyc"

genai.configure(api_key="AIzaSyCw2EGbX55HV5PcqVVjS2LV0nXi8awGEEQ")
model = genai.GenerativeModel("gemini-1.5-flash")

# Load credentials from a JSON file
key_path = "data-driven-cx-04da37b60712.json"  # Update this with the correct path
credentials = service_account.Credentials.from_service_account_file(key_path)

# Set up BigQuery client
project_id = 'data-driven-cx'
client = bigquery.Client(credentials=credentials, project=project_id)

# Initialize Speech-to-Text client
speech_client = speech.SpeechClient(credentials=credentials)

# Set your project ID and dataset ID
project_id = "data-driven-cx"
dataset_id = "agentic_ai"

# Function to fetch table schemas
def fetch_table_schemas(project_id, dataset_id):
    dataset_ref = client.dataset(dataset_id)
    tables = client.list_tables(dataset_ref)

    all_schemas_info = ""
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        try:
            table = client.get_table(table_ref)
            schema_str = f"Schema for table {table.table_id}:\n"
            for field in table.schema:
                schema_str += f"  {field.name} ({field.field_type})\n"
            all_schemas_info += schema_str + "\n"
        except Exception as e:
            print(f"Table {table.table_id} not found.")
    
    return all_schemas_info


schema_for_tables = fetch_table_schemas(project_id, dataset_id)


# Function to execute SQL queries
def execute_query(query):
    try:
        query_job = client.query(query)
        results = query_job.result().to_dataframe()
        return results
    except Exception as e:
        print(f"Query execution error: {e}")
        return None

def mail_sender(receiver_email, subject, body):
    """Send email using Gmail SMTP"""
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def gen_response(prompt):
    response = model.generate_content(prompt)
    print(response.text)
    return response.text


async def process_text(update: Update, text: str):
    user_input = update.message.text
    print(user_input)
    user = update.message.from_user
    prompt_for_routing_agent =f"""As the leader of a dynamic team of specialized agents in a restaurant, your mission is to strategically allocate tasks to achieve the optimal outcome for the user query. You have the following agents at your disposal:

1) SQL Generator - for crafting precise database queries.
2) Summary Generator - for distilling information into concise summaries.
3) Mail Generator - for composing effective email communications.
4) Mail Sender - for ensuring timely delivery of emails.
5)SQL Executor
6)Support Agent                                    


Your response should clearly outline the sequence in which these agents will operate to address the user query efficiently. just 
just reply the name of requred agents in sequince.
Here is the user query:
{text}
"""
    agents=gen_response(prompt_for_routing_agent)
    prompt_to_generate_sql=f"""Act a sql writer for bigquery, write sql on the basis of user input,
here is the schema of my daatabase in my database.
project_id = "data-driven-cx"
dataset_id = "agentic_ai"

here is the schema:
{schema_for_tables}

here is the is the user input
{text}
write only executable query for bigquery, dont add any additional comment.
"""
    if 'SQL Generator' in agents:
        sql=gen_response(prompt_to_generate_sql)
        sql=re.sub(r"```sql|```", "", sql).strip()
        result=execute_query(sql)
        prompt_for_summary_gen=f"""act as a summary generator agent, an another agent called  sql genertor fetched data on the basis of user query.
    now your task is generate summary to send final respone to the user  on the basis of agent output and user query.
    here is the user query and agent response. 
    user query=
    {text}

    agent response=
    {sql} 
    {result}
    ***reply wit very concise message***"""
        
    if 'Summary Generator' in agents:
        summary=gen_response(prompt_for_summary_gen)
        await update.message.reply_text(summary)
    if 'Support Agent' in agents:
        prompt_for_support_agent=f"""Act as a customer support in a restaurant. reply to the customer on the basis of user query. reply with very short and concise answer.
        here is the user query:
        {text}
        """
        support_output=gen_response(prompt_for_support_agent)
        await update.message.reply_text(support_output)
    if 'Mail Generator' in agents:
        user = update.message.from_user
        # Get user inputs
        # receiver_email = input("Enter recipient's email: ")
        # email_type = input("What type of email do you want to generate? (e.g., formal, informal, meeting request): ")
        # context = input("Provide context for the email: ")
        
        # Create prompt for AI
        prompt = f"""Generate a email with the following context: {text}
        Please provide the To, subject line and body separately, formatted as:
        TO:[receiver email]
        SUBJECT: [subject here]
        BODY: [body here]
        sender name is
        {user.first_name}"""
        
        # Generate email content
        generated_content = gen_response(prompt)
        
        if generated_content:
    # Parse the generated content
            try:
                lines = generated_content.splitlines()
                receiver_email = None
                subject = None
                body_start_index = None
                
                for i, line in enumerate(lines):
                    if line.startswith("TO:"):
                        receiver_email = line.replace("TO:", "").strip()
                    elif line.startswith("SUBJECT:"):
                        subject = line.replace("SUBJECT:", "").strip()
                    elif line.startswith("BODY:"):
                        body_start_index = i
                        break  # Stop looping after finding BODY

                if body_start_index is not None:
                    body = "\n".join(lines[body_start_index + 1:]).strip()
                else:
                    raise ValueError("BODY section not found")

                if receiver_email and subject and body:
                    # Send the email
                    mail_sender(receiver_email, subject, body)
                    await update.message.reply_text(generated_content)
                else:
                    raise ValueError("Missing email components")

            except Exception as e:
                print(f"Error parsing generated content: {e}")

async def handle_text(update: Update, context: CallbackContext):
    user_input = update.message.text
    await process_text(update, user_input)


async def handle_voice(update: Update, context: CallbackContext):
    file = await update.message.voice.get_file()
    file_path = f"voice_{update.message.message_id}.ogg"
    
    # Download voice file
    await file.download_to_drive(file_path)

    # Convert voice to text
    transcript = transcribe_audio(file_path)

    if transcript:
        await process_text(update, transcript)
    else:
        await update.message.reply_text("Sorry, I couldn't understand the voice message.")

    # Clean up the file
    os.remove(file_path)


def transcribe_audio(file_path):
    """Converts speech to text using Google Cloud Speech-to-Text"""
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US"
    )

    response = speech_client.recognize(config=config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript
    return None


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))


    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
