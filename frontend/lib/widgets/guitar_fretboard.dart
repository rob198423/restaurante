import 'package:flutter/material.dart';

import '../core/theme.dart';

class GuitarFretboard extends StatelessWidget {
  const GuitarFretboard({super.key, required this.tablature});

  final Map<String, dynamic> tablature;

  @override
  Widget build(BuildContext context) {
    final lines = (tablature['lines'] as List<dynamic>? ?? []).take(8).toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Guitar neck', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 16),
        AspectRatio(
          aspectRatio: 2.8,
          child: CustomPaint(painter: _FretboardPainter(lines)),
        ),
      ],
    );
  }
}

class _FretboardPainter extends CustomPainter {
  _FretboardPainter(this.lines);
  final List<dynamic> lines;

  @override
  void paint(Canvas canvas, Size size) {
    final stringPaint = Paint()..color = Colors.white24..strokeWidth = 2;
    final fretPaint = Paint()..color = Colors.white12..strokeWidth = 3;
    final notePaint = Paint()..color = toneCyan;
    for (var i = 0; i < 6; i++) {
      final y = size.height * (i + 1) / 7;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), stringPaint);
    }
    for (var i = 0; i <= 12; i++) {
      final x = size.width * i / 12;
      canvas.drawLine(Offset(x, size.height / 8), Offset(x, size.height * 7 / 8), fretPaint);
    }
    for (final item in lines) {
      final notes = item is Map ? (item['notes'] as List<dynamic>? ?? []) : [];
      for (final note in notes) {
        if (note is! Map) continue;
        final string = ['E', 'A', 'D', 'G', 'B', 'e'].indexOf(note['string'].toString());
        final fret = (note['fret'] as num?)?.toInt() ?? 0;
        if (string < 0) continue;
        final x = size.width * (fret.clamp(0, 12) + 0.5) / 12;
        final y = size.height * (string + 1) / 7;
        canvas.drawCircle(Offset(x, y), 9, notePaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _FretboardPainter oldDelegate) => oldDelegate.lines != lines;
}
