import 'package:flutter/material.dart';

import '../models/analysis_result.dart';
import '../widgets/audio_player_card.dart';
import '../widgets/chord_chip.dart';
import '../widgets/guitar_fretboard.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({required this.result, required this.localPath, super.key});

  final AnalysisResult result;
  final String localPath;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Resultado')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          AudioPlayerCard(localPath: localPath, filename: result.filename),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _Metric(label: 'Tom', value: result.detectedKey),
                  _Metric(label: 'BPM', value: result.bpm.toStringAsFixed(1)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'Acordes',
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [for (final chord in result.chords) ChordChip(label: chord)],
            ),
          ),
          _Section(
            title: 'Escalas compatíveis',
            child: Column(
              children: [
                for (final scale in result.compatibleScales)
                  ListTile(
                    leading: const Icon(Icons.scale),
                    title: Text(scale),
                  ),
              ],
            ),
          ),
          _Section(
            title: 'Braço da guitarra',
            child: GuitarFretboard(notes: result.tablature),
          ),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 6),
        Text(value, style: Theme.of(context).textTheme.headlineMedium),
      ],
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 14),
            child,
          ],
        ),
      ),
    );
  }
}
