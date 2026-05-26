import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/api_client.dart';
import '../models/track.dart';
import '../widgets/glass_card.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<Track>> future = context.read<ApiClient>().tracks();

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => setState(() => future = context.read<ApiClient>().tracks()),
      child: FutureBuilder<List<Track>>(
        future: future,
        builder: (context, snapshot) {
          final tracks = snapshot.data ?? [];
          return ListView(
            padding: const EdgeInsets.all(22),
            children: [
              GlassCard(child: Text('History', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900))),
              const SizedBox(height: 12),
              if (snapshot.connectionState == ConnectionState.waiting) const LinearProgressIndicator(),
              for (final track in tracks)
                Card(
                  child: ListTile(
                    leading: Icon(track.mediaType == 'video' ? Icons.movie_rounded : Icons.music_note_rounded),
                    title: Text(track.title),
                    subtitle: Text('${track.status} - ${DateFormat.yMMMd().add_Hm().format(track.createdAt)}'),
                    trailing: Text(track.sourceFilename, overflow: TextOverflow.ellipsis),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
