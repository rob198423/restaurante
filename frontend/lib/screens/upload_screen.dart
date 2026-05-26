import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';

import '../core/api_client.dart';
import '../widgets/glass_card.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final title = TextEditingController(text: 'New Tonemind Session');
  final recorder = AudioRecorder();
  bool busy = false;
  bool recording = false;
  String? message;

  @override
  void dispose() {
    recorder.dispose();
    super.dispose();
  }

  Future<void> pickAndUpload(FileType type) async {
    final result = await FilePicker.platform.pickFiles(type: type);
    final path = result?.files.single.path;
    if (path == null) return;
    await upload(File(path));
  }

  Future<void> toggleRecording() async {
    if (recording) {
      final path = await recorder.stop();
      setState(() => recording = false);
      if (path != null) await upload(File(path));
      return;
    }
    if (!await recorder.hasPermission()) {
      setState(() => message = 'Microphone permission denied');
      return;
    }
    final dir = await getTemporaryDirectory();
    final path = '${dir.path}/tonemind_recording_${DateTime.now().millisecondsSinceEpoch}.wav';
    await recorder.start(const RecordConfig(encoder: AudioEncoder.wav), path: path);
    setState(() {
      recording = true;
      message = 'Recording microphone... tap again to upload';
    });
  }

  Future<void> upload(File file) async {
    setState(() {
      busy = true;
      message = null;
    });
    try {
      final api = context.read<ApiClient>();
      final track = await api.uploadTrack(title: title.text, file: file);
      setState(() => message = 'Uploaded ${track.title}. Open Analysis to process it.');
    } catch (err) {
      setState(() => message = err.toString());
    } finally {
      setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(22),
      children: [
        GlassCard(
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text('Upload source', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
            const SizedBox(height: 12),
            TextField(controller: title, decoration: const InputDecoration(labelText: 'Session title')),
            const SizedBox(height: 16),
            Wrap(spacing: 12, runSpacing: 12, children: [
              ElevatedButton.icon(onPressed: busy ? null : () => pickAndUpload(FileType.audio), icon: const Icon(Icons.library_music_rounded), label: const Text('Upload MP3/audio')),
              ElevatedButton.icon(onPressed: busy ? null : () => pickAndUpload(FileType.video), icon: const Icon(Icons.video_library_rounded), label: const Text('Upload video')),
              ElevatedButton.icon(onPressed: busy ? null : toggleRecording, icon: Icon(recording ? Icons.stop_circle_rounded : Icons.mic_rounded), label: Text(recording ? 'Stop and upload' : 'Record microphone')),
            ]),
            if (busy) const Padding(padding: EdgeInsets.only(top: 18), child: LinearProgressIndicator()),
            if (message != null) Padding(padding: const EdgeInsets.only(top: 18), child: Text(message!)),
          ]),
        ),
      ],
    );
  }
}
