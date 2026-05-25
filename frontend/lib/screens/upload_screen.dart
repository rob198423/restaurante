import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../core/api_client.dart';
import 'result_screen.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({required this.apiClient, super.key});

  final ApiClient apiClient;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  bool _isUploading = false;

  Future<void> _pickAndUpload() async {
    final picked = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['mp3', 'wav', 'm4a', 'aac', 'flac'],
    );
    final path = picked?.files.single.path;
    if (path == null) return;

    setState(() => _isUploading = true);
    try {
      final result = await widget.apiClient.uploadAudio(File(path));
      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result, localPath: path)),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Falha no upload: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload MP3')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Center(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.library_music, size: 72),
                  const SizedBox(height: 16),
                  Text('Analise sua música', style: Theme.of(context).textTheme.headlineSmall),
                  const SizedBox(height: 12),
                  const Text(
                    'O arquivo é enviado ao FastAPI, salvo no storage e processado pela camada de IA.',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _isUploading ? null : _pickAndUpload,
                    icon: const Icon(Icons.file_upload),
                    label: Text(_isUploading ? 'Analisando...' : 'Escolher arquivo'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
