import json
import os
import base64

# Paths
CHATGPT_EXPORT_PATH = "chatgpt-export/conversations.json"
OUTPUT_PATH = "converted_openwebui.json"
IMAGE_FOLDERS = ["chatgpt-export/", "chatgpt-export/dalle-generations/"]

def map_images():
    """Scan images and create a lookup dictionary."""
    image_map = {}
    for folder in IMAGE_FOLDERS:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.startswith("file-"):
                file_id = filename.split("-")[1].split(".")[0]  # Extract base ID
                image_map[file_id] = os.path.join(folder, filename)
    return image_map

def encode_image_base64(image_path, mime_type="image/jpeg"):
    """Convert an image file to a Base64-encoded data URL."""
    try:
        with open(image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        print(f"⚠️ ERROR encoding {image_path}: {e}")
        return None

def find_image_path(asset_pointer, image_map):
    """Find the real file for an asset_pointer."""
    filename_id = asset_pointer.split("/")[-1].replace("file-", "")
    for key in image_map:
        if key.startswith(filename_id):
            return image_map[key]
    return None  # Not found

def convert_conversations(chatgpt_data, image_map):
    openwebui_chats = []

    for chat in chatgpt_data:
        messages = []
        models_used = set()  # Track all models used in the conversation

        for node_id, node in chat.get("mapping", {}).items():
            message_data = node.get("message")
            if not message_data:
                continue  # Skip if there's no message data

            content_type = message_data.get("content", {}).get("content_type", None)
            content_parts = message_data.get("content", {}).get("parts", None)

            role = message_data.get("author", {}).get("role", "unknown")  # Default to unknown role

            # Extract model info
            metadata = message_data.get("metadata", {})
            model_slug = metadata.get("model_slug") or metadata.get("default_model_slug") or None
            if model_slug:
                models_used.add(model_slug)  # Store the model name at conversation level

            # Extract text & attachments conditions checked
            text_content = ""
            files = []  # OpenWebUI expects this

            if content_type == "text" and content_parts:
                text_content = " ".join(content_parts).strip()

            elif content_type == "multimodal_text" and content_parts:
                for part in content_parts:
                    if isinstance(part, dict) and "asset_pointer" in part:
                        image_path = find_image_path(part["asset_pointer"], image_map)
                        filename = os.path.basename(part["asset_pointer"])

                        if image_path:
                            mime_type = part.get("mime_type", "image/jpeg")
                            encoded_data = encode_image_base64(image_path, mime_type)
                            if encoded_data:
                                files.append({
                                    "type": "image",
                                    "name": filename,
                                    "url": encoded_data  # OpenWebUI expects Base64 URLs
                                })
                        else:
                            print(f"⚠️ WARNING: Couldn't find or encode {filename}")

                    elif isinstance(part, str):
                        text_content += f" {part}"  # Preserve accompanying text

                text_content = text_content.strip()

            # Add message ONLY if there is text or an image
            if text_content or files:
                message_entry = {
                    "role": role,
                    "content": text_content if text_content else "",
                    "files": files,  # OpenWebUI expects "files"
                    "timestamp": message_data.get("create_time"),
                }

                # If the message is from the assistant, add `model` and `modelName`
                if role == "assistant" and model_slug:
                    message_entry["model"] = model_slug
                    message_entry["modelName"] = model_slug

                messages.append(message_entry)

        # Ensure at least one model is listed for conversation-level `models: []`
        models_list = list(models_used) if models_used else ["unknown"]

        openwebui_chats.append({
            "title": chat.get("title", "Untitled Chat"),
            "models": models_list,  # Correct place for model names at conversation level
            "create_time": chat.get("create_time"),
            "update_time": chat.get("update_time"),
            "messages": messages
        })

    return openwebui_chats

# Step 1: Scan for images
image_map = map_images()

# Step 2: Load ChatGPT export
with open(CHATGPT_EXPORT_PATH, "r", encoding="utf-8") as f:
    chatgpt_conversations = json.load(f)

# Step 3: Convert data
openwebui_data = convert_conversations(chatgpt_conversations, image_map)

# Step 4: Save output
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(openwebui_data, f, indent=4, ensure_ascii=False)

print(f"✅ FINAL FIXED CONVERSION COMPLETED! Saved as {OUTPUT_PATH}")