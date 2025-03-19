# chatgpt-openwebui-converter
Convert ChatGPT conversations so they can be imported into Open WebUI.

Open WebUI doesn't import chatGPT conversations correctly. I searched for a conversion tool but couldn't find one, so I had chatGPT make me this. It preserves uploaded and generated images and model names, which don't get imported properly if you just try to import conversations.json as it came from openAI. It's not perfect, there's some weirdness around generated images for example, but it was good enough for me.

How to use:
1. Export your chatGPT data and download the zip file. It's in Settings, under Data controls.
2. Download import.py and in the same directory create a subdirectory called chatgpt-export
3. Unzip the file you downloaded from openAI into chatgpt-export/
4. Run import.py (I used Python 3.10 on Windows). It looks for conversations.json and any images you have uploaded or generated (in chatgpt-export/ and chatgpt-export/dalle-generations/)
5. If it's succesful, it will generate converted-openwebui.json which can be imported into Open WebUI.
6. If it prints errors, have chatGPT debug them for you.

I recommend setting up a throwaway instance of Open WebUI and testing the import there (it's what I did). For example, I noticed that I had to move some conversations into folders in Open WebUI before importing more, or some earlier chats would just disappear.
