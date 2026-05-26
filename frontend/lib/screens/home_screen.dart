import 'package:flutter/material.dart';

import '../core/theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/metric_tile.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(22),
      children: [
        GlassCard(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Professional AI music workstation', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w900)),
            const SizedBox(height: 8),
            Text('Upload songs, videos, or microphone takes to extract key, BPM, chords, scales, Greek modes, tabs, stems, solos, arpeggios, MIDI, PDF, and Guitar Pro GPIF.', style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.white70)),
            const SizedBox(height: 18),
            Wrap(spacing: 12, runSpacing: 12, children: const [
              Chip(label: Text('librosa')),
              Chip(label: Text('Demucs')),
              Chip(label: Text('Basic Pitch')),
              Chip(label: Text('Essentia')),
              Chip(label: Text('PyTorch')),
              Chip(label: Text('FFmpeg')),
            ]),
          ]),
        ),
        const SizedBox(height: 16),
        LayoutBuilder(builder: (context, constraints) {
          final width = constraints.maxWidth > 700 ? (constraints.maxWidth - 24) / 3 : constraints.maxWidth;
          return Wrap(spacing: 12, runSpacing: 12, children: [
            SizedBox(width: width, child: const MetricTile(label: 'Detection', value: 'Key + BPM', icon: Icons.radar_rounded, color: toneCyan)),
            SizedBox(width: width, child: const MetricTile(label: 'Harmony', value: 'Chords + Modes', icon: Icons.piano_rounded, color: toneAccent)),
            SizedBox(width: width, child: const MetricTile(label: 'Exports', value: 'MIDI PDF GPIF', icon: Icons.ios_share_rounded, color: toneGreen)),
          ]);
        }),
      ],
    );
  }
}
