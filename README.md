
If you've ever forgotten to close or unload Comfyui before starting something else that uses the video card like a game, LLM and found it very slow.  This is because ComfyUI is still using the VRAM even though you are not using it.

Unloads the models from the VRAM when after nothing is running for 15 minutes.  Like Ollama does.

You can set the number of seconds in the settings.
