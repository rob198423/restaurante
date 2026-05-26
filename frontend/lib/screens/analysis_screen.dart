import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../core/theme.dart';
import '../models/analysis.dart';
import '../models/track.dart';
import '../widgets/glass_card.dart';
import '../widgets/guitar_fretboard.dart';
import '../widgets/metric_tile.dart';

class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  List<Track> tracks = [];
  Track? selected;
  AnalysisResult? result;
  bool busy = false;
  String? message;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    setState(() => busy = true);
    try {
      tracks = await context.read<ApiClient>().tracks();
      selected ??= tracks.isNotEmpty ? tracks.first : null;
    } catch (err) {
      message = err.toString();
    } finally {
      setState(() => busy = false);
    }
  }

  Future<void> analyze() async {
    final track = selected;
    if (track == null) return;
    setState(() {
      busy = true;
      message = 'Analyzing audio with TONEMIND AI...';
    });
    try {
      result = await context.read<ApiClient>().analyze(track.id);
      message = 'Analysis complete';
      await refresh();
    } catch (err) {
      message = err.toString();
    } finally {
      setState(() => busy = false);
    }
  }

  Future<void> separate() async {
    final track = selected;
    if (track == null) return;
    setState(() => busy = true);
    try {
      result = await context.read<ApiClient>().separate(track.id);
      message = 'Instrument stems rendered';
    } catch (err) {
      message = err.toString();
    } finally {
      setState(() => busy = false);
    }
  }

  Future<void> export(String format) async {
    final track = selected;
    if (track == null) return;
    setState(() => busy = true);
    try {
      final bytes = await context.read<ApiClient>().exportTrack(track.id, format);
      final dir = await getApplicationDocumentsDirectory();
      final extension = format == 'guitarpro' ? 'gpif' : format;
      final file = File('${dir.path}/${track.title.replaceAll(' ', '_')}.$extension');
      await file.writeAsBytes(bytes);
      message = 'Saved ${file.path}';
    } catch (err) {
      message = err.toString();
    } finally {
      setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: refresh,
      child: ListView(
        padding: const EdgeInsets.all(22),
        children: [
          GlassCard(
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              Text('Analysis console', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
              const SizedBox(height: 12),
              DropdownButtonFormField<Track>(
                value: selected,
                items: tracks.map((track) => DropdownMenuItem(value: track, child: Text('${track.title} - ${track.status}'))).toList(),
                onChanged: (track) => setState(() {
                  selected = track;
                  result = null;
                }),
                decoration: const InputDecoration(labelText: 'Track'),
              ),
              const SizedBox(height: 12),
              Wrap(spacing: 12, runSpacing: 12, children: [
                ElevatedButton.icon(onPressed: busy ? null : analyze, icon: const Icon(Icons.auto_awesome_rounded), label: const Text('Detect music')),
                ElevatedButton.icon(onPressed: busy ? null : separate, icon: const Icon(Icons.hub_rounded), label: const Text('Separate instruments')),
                OutlinedButton.icon(onPressed: busy ? null : () => export('midi'), icon: const Icon(Icons.piano_rounded), label: const Text('MIDI')),
                OutlinedButton.icon(onPressed: busy ? null : () => export('guitarpro'), icon: const Icon(Icons.music_note_rounded), label: const Text('Guitar Pro')),
                OutlinedButton.icon(onPressed: busy ? null : () => export('pdf'), icon: const Icon(Icons.picture_as_pdf_rounded), label: const Text('PDF')),
              ]),
              if (busy) const Padding(padding: EdgeInsets.only(top: 16), child: LinearProgressIndicator()),
              if (message != null) Padding(padding: const EdgeInsets.only(top: 12), child: Text(message!)),
            ]),
          ),
          const SizedBox(height: 16),
          if (result != null) _AnalysisView(result: result!),
        ],
      ),
    );
  }
}

class _AnalysisView extends StatelessWidget {
  const _AnalysisView({required this.result});
  final AnalysisResult result;

  @override
  Widget build(BuildContext context) {
    final summary = result.summary;
    return Column(children: [
      LayoutBuilder(builder: (context, constraints) {
        final width = constraints.maxWidth > 700 ? (constraints.maxWidth - 24) / 3 : constraints.maxWidth;
        return Wrap(spacing: 12, runSpacing: 12, children: [
          SizedBox(width: width, child: MetricTile(label: 'Key', value: summary['key'].toString(), icon: Icons.key_rounded, color: toneCyan)),
          SizedBox(width: width, child: MetricTile(label: 'BPM', value: summary['bpm'].toString(), icon: Icons.speed_rounded, color: toneGreen)),
          SizedBox(width: width, child: MetricTile(label: 'Mode', value: summary['primary_mode'].toString(), icon: Icons.blur_circular_rounded, color: toneAccent)),
        ]);
      }),
      const SizedBox(height: 16),
      GlassCard(child: GuitarFretboard(tablature: result.tablature)),
      const SizedBox(height: 16),
      GlassCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Chords', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),
          Wrap(spacing: 8, runSpacing: 8, children: result.chords.take(36).map((chord) => Chip(label: Text('${chord['chord']}  ${chord['start']}s'))).toList()),
          const Divider(height: 32),
          Text('Greek modes', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
          ...result.modes.map((mode) => ListTile(contentPadding: EdgeInsets.zero, title: Text(mode['name'].toString()), subtitle: Text((mode['notes'] as List<dynamic>).join(' - ')))),
        ]),
      ),
    ]);
  }
}
