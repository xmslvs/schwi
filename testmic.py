from RealtimeSTT import AudioToTextRecorder

recorder = AudioToTextRecorder(input_device_index=0)

print("Say something...")
text = recorder.text()
print("Heard:", text)