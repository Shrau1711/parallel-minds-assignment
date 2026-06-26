from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL, INPUT_COST_PER_1K, OUTPUT_COST_PER_1K
from tools.summarizer import summarize
from tools.sentiment import analyze_sentiment
from tools.code_explainer import explain_code
from tools.youtube_tool import fetch_youtube_transcript, detect_youtube_url
import tiktoken

client = genai.Client(api_key=GEMINI_API_KEY)

# used for token counting to estimate cost
encoder = tiktoken.get_encoding("cl100k_base")

def estimate_cost(text: str) -> dict:
    """Estimate Gemini API cost before running the full plan."""
    token_count = len(encoder.encode(text))
    input_cost = (token_count / 1000) * INPUT_COST_PER_1K
    # rough estimate: output is usually ~30% of input length
    output_cost = (token_count * 0.3 / 1000) * OUTPUT_COST_PER_1K
    total = round(input_cost + output_cost, 6)
    return {
        "estimated_tokens": token_count,
        "estimated_cost_usd": total
    }

def determine_intent(combined_text: str, user_query: str) -> dict:
    """Ask Gemini to figure out what the user wants and plan the tool sequence."""
    
    prompt = f"""
    You are an intent detection system for an agentic AI app.
    
    The user has provided the following extracted content:
    ---
    {combined_text[:3000]}
    ---
    
    The user's query is: "{user_query}"
    
    Based on the content and query, decide:
    1. Is there enough information to act? (yes/no)
    2. If no, what follow-up question should be asked?
    3. If yes, what is the ordered list of tools to run?
    
    Available tools: summarize, sentiment, code_explain, youtube_transcript, conversational, cross_input_reasoning
    
    Respond in exactly this format:
    CLEAR: <yes or no>
    FOLLOWUP: <follow up question if CLEAR is no, else 'none'>
    TOOLS: <comma separated list of tools to run in order>
    REASONING: <one sentence explaining your plan>
    """
    
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw = response.text.strip()
    
    result = {"clear": "yes", "followup": "none", "tools": [], "reasoning": ""}
    
    for line in raw.split("\n"):
        if line.startswith("CLEAR:"):
            result["clear"] = line.replace("CLEAR:", "").strip().lower()
        elif line.startswith("FOLLOWUP:"):
            result["followup"] = line.replace("FOLLOWUP:", "").strip()
        elif line.startswith("TOOLS:"):
            tools_raw = line.replace("TOOLS:", "").strip()
            result["tools"] = [t.strip() for t in tools_raw.split(",")]
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.replace("REASONING:", "").strip()
    
    return result

def run_agent(extracted_inputs: dict, user_query: str) -> dict:
    """
    Main agent function. Takes all extracted content + user query,
    plans the tool sequence, executes it, returns result + trace.
    """
    
    trace = []  # tracks every step taken — shown in UI
    
    # combine all extracted text into one context string
    combined_text = ""
    for source, content in extracted_inputs.items():
        if content.get("text"):
            combined_text += f"\n[{source}]\n{content['text']}\n"
    
    if not combined_text.strip() and not user_query.strip():
        return {
            "followup": "I didn't receive any content or query. Could you clarify what you'd like help with?",
            "trace": trace,
            "result": None
        }
    
    # step 1: estimate cost before doing anything
    cost_info = estimate_cost(combined_text + user_query)
    trace.append(f"Cost estimate: ~{cost_info['estimated_tokens']} tokens, ~${cost_info['estimated_cost_usd']} USD")
    
    # step 2: detect youtube url anywhere in the inputs
    youtube_url = detect_youtube_url(combined_text) or detect_youtube_url(user_query)
    if youtube_url:
        trace.append(f"YouTube URL detected: {youtube_url}")
    
    # step 3: determine intent and plan
    trace.append("Analyzing intent and planning tool sequence...")
    intent = determine_intent(combined_text, user_query)
    trace.append(f"Plan: {intent['reasoning']}")
    trace.append(f"Tools to run: {', '.join(intent['tools'])}")
    
    # step 4: if not enough info, ask follow up
    if intent["clear"] == "no":
        return {
            "followup": intent["followup"],
            "trace": trace,
            "result": None
        }
    
    # step 5: execute tools in planned order
    final_result = {}
    
    for tool in intent["tools"]:
        
        if tool == "summarize":
            trace.append("Running summarizer...")
            text_to_summarize = combined_text if combined_text.strip() else user_query
            final_result["summary"] = summarize(text_to_summarize)
            trace.append("Summarization complete")
        
        elif tool == "sentiment":
            trace.append("Running sentiment analysis...")
            text_to_analyze = combined_text if combined_text.strip() else user_query
            final_result["sentiment"] = analyze_sentiment(text_to_analyze)
            trace.append("Sentiment analysis complete")
        
        elif tool == "code_explain":
            trace.append("Running code explainer...")
            final_result["code_explanation"] = explain_code(combined_text)
            trace.append("Code explanation complete")
        
        elif tool == "youtube_transcript":
            if youtube_url:
                trace.append(f"▶Fetching YouTube transcript...")
                yt_result = fetch_youtube_transcript(youtube_url)
                if yt_result.get("text"):
                    # add transcript to context and summarize it
                    combined_text += f"\n[YouTube Transcript]\n{yt_result['text']}\n"
                    trace.append("Summarizing YouTube transcript...")
                    final_result["youtube_summary"] = summarize(yt_result["text"])
                    final_result["youtube_duration"] = yt_result.get("duration", "unknown")
                    trace.append("YouTube transcript fetched and summarized")
                else:
                    final_result["youtube_error"] = yt_result.get("error", "Failed to fetch transcript")
                    trace.append(f"YouTube fetch failed: {final_result['youtube_error']}")
        
        elif tool == "conversational":
            try:
                trace.append("[RUNNING] Generating conversational response")
                convo_prompt = f"""You are an intelligent agentic assistant built with FastAPI and Gemini.
                You can process text, PDFs, images, and audio files. You can summarize, analyze sentiment, explain code, fetch YouTube transcripts, and reason across multiple inputs.

                The user asked: {user_query}
                Context: {combined_text[:2000]}

                Respond helpfully and concisely. Do not use markdown formatting or asterisks. Use plain sentences only."""
                response = client.models.generate_content(model=GEMINI_MODEL, contents=convo_prompt)
                final_result["answer"] = response.text.strip()
                trace.append("[DONE] Response generated")
            except Exception as e:
                trace.append(f"[ERROR] Conversational response failed: {str(e)}")
                final_result["answer"] = "Sorry, I could not generate a response right now."
        
        elif tool == "cross_input_reasoning":
            try:
                trace.append("[RUNNING] Cross-input reasoning")
                reasoning_prompt = f"""
                The user has provided multiple inputs and wants a unified analysis.
                
                Combined content:
                {combined_text[:4000]}
                
                User query: {user_query}
                
                Provide a thorough comparative analysis answering the user's query directly. Do not use markdown formatting or asterisks. Use plain sentences only.
                """
                response = client.models.generate_content(model=GEMINI_MODEL, contents=reasoning_prompt)
                final_result["cross_input_analysis"] = response.text.strip()
                trace.append("[DONE] Cross-input reasoning complete")
            except Exception as e:
                trace.append(f"[ERROR] Cross-input reasoning failed: {str(e)}")
                final_result["cross_input_error"] = str(e)
    
    return {
        "followup": None,
        "trace": trace,
        "result": final_result,
        "cost": cost_info
    }