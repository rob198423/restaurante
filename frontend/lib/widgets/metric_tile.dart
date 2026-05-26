import 'package:flutter/material.dart';

import '../core/theme.dart';

class MetricTile extends StatelessWidget {
  const MetricTile({super.key, required this.label, required this.value, required this.icon, this.color = toneCyan});

  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(color: tonePanelSoft, borderRadius: BorderRadius.circular(22)),
      child: Row(
        children: [
          CircleAvatar(backgroundColor: color.withOpacity(0.16), foregroundColor: color, child: Icon(icon)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(label, style: Theme.of(context).textTheme.labelLarge?.copyWith(color: Colors.white60)),
              const SizedBox(height: 4),
              Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
            ]),
          ),
        ],
      ),
    );
  }
}
