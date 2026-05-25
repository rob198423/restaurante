import 'package:flutter/material.dart';

import '../models/analysis_result.dart';

class GuitarFretboard extends StatelessWidget {
  const GuitarFretboard({required this.notes, super.key});

  final List<TabNote> notes;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final note in notes)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Row(
              children: [
                SizedBox(width: 28, child: Text('S${note.stringNumber}')),
                Expanded(
                  child: Stack(
                    alignment: Alignment.centerLeft,
                    children: [
                      Container(height: 2, color: Colors.white24),
                      FractionallySizedBox(
                        widthFactor: (note.fret + 1) / 13,
                        child: Align(
                          alignment: Alignment.centerRight,
                          child: CircleAvatar(
                            radius: 14,
                            child: Text('${note.fret}', style: const TextStyle(fontSize: 12)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Text(note.note),
              ],
            ),
          ),
      ],
    );
  }
}
