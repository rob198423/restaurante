import 'package:flutter/material.dart';

class ChordChip extends StatelessWidget {
  const ChordChip({required this.label, super.key});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(label),
      avatar: const Icon(Icons.music_note, size: 18),
      backgroundColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.14),
      side: BorderSide(color: Theme.of(context).colorScheme.primary),
    );
  }
}
