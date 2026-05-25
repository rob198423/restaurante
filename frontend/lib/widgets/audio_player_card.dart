import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';

class AudioPlayerCard extends StatefulWidget {
  const AudioPlayerCard({required this.localPath, required this.filename, super.key});

  final String localPath;
  final String filename;

  @override
  State<AudioPlayerCard> createState() => _AudioPlayerCardState();
}

class _AudioPlayerCardState extends State<AudioPlayerCard> {
  final _player = AudioPlayer();
  bool _isPlaying = false;

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  Future<void> _toggle() async {
    if (_isPlaying) {
      await _player.pause();
    } else {
      await _player.play(DeviceFileSource(widget.localPath));
    }
    setState(() => _isPlaying = !_isPlaying);
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: IconButton(
          icon: Icon(_isPlaying ? Icons.pause_circle : Icons.play_circle, size: 42),
          onPressed: _toggle,
        ),
        title: Text(widget.filename),
        subtitle: const Text('Player local do arquivo enviado'),
      ),
    );
  }
}
