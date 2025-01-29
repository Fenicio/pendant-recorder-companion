import whisperx

# This will trigger the model download if it hasn't been downloaded yet
model = whisperx.load_model("base", device="cpu", compute_type="int8")
print("Model loaded successfully!")
