import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../widgets/glass_card.dart';

class ToolsScreen extends StatefulWidget {
  const ToolsScreen({super.key});

  @override
  State<ToolsScreen> createState() => _ToolsScreenState();
}

class _ToolsScreenState extends State<ToolsScreen> {
  final frequency = TextEditingController(text: '440');
  final bpm = TextEditingController(text: '120');
  Map<String, dynamic>? tuner;
  Map<String, dynamic>? metro;
  String? message;

  Future<void> tune() async {
    try {
      tuner = await context.read<ApiClient>().tuner(double.parse(frequency.text));
      setState(() => message = null);
    } catch (err) {
      setState(() => message = err.toString());
    }
  }

  Future<void> metronome() async {
    try {
      metro = await context.read<ApiClient>().metronome(int.parse(bpm.text), 4, 4);
      setState(() => message = null);
    } catch (err) {
      setState(() => message = err.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(22), children: [
      GlassCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('Tuner', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 12),
          TextField(controller: frequency, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Frequency Hz')),
          const SizedBox(height: 12),
          ElevatedButton.icon(onPressed: tune, icon: const Icon(Icons.tune_rounded), label: const Text('Analyze pitch')),
          if (tuner != null) ListTile(title: Text('${tuner!['note']}${tuner!['octave']}'), subtitle: Text('${tuner!['cents']} cents - target ${tuner!['target_hz']} Hz')),
        ]),
      ),
      const SizedBox(height: 16),
      GlassCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Text('Metronome', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 12),
          TextField(controller: bpm, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'BPM')),
          const SizedBox(height: 12),
          ElevatedButton.icon(onPressed: metronome, icon: const Icon(Icons.av_timer_rounded), label: const Text('Generate click map')),
          if (metro != null) Wrap(spacing: 8, runSpacing: 8, children: (metro!['beats'] as List<dynamic>).map((beat) => Chip(label: Text(beat['accent'] == true ? 'DOWN ${beat['index']}' : '${beat['index']}'))).toList()),
          if (message != null) Text(message!),
        ]),
      ),
    ]);
  }
}
