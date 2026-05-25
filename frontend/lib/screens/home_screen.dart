import 'package:flutter/material.dart';

import '../core/api_client.dart';
import 'upload_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({required this.apiClient, super.key});

  final ApiClient apiClient;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ToneMind AI')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('MVP Studio', style: Theme.of(context).textTheme.headlineSmall),
                    const SizedBox(height: 12),
                    const Text(
                      'Envie um MP3 para detectar tom, BPM, acordes, escalas compatíveis e uma tablatura inicial.',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => UploadScreen(apiClient: apiClient)),
              ),
              icon: const Icon(Icons.upload_file),
              label: const Text('Enviar MP3'),
            ),
            const SizedBox(height: 16),
            const _FeatureList(),
          ],
        ),
      ),
    );
  }
}

class _FeatureList extends StatelessWidget {
  const _FeatureList();

  @override
  Widget build(BuildContext context) {
    const features = [
      'Detecção de tom com Librosa',
      'BPM automático',
      'Acordes diatônicos',
      'Escalas e modos compatíveis',
      'Tablatura simples para guitarra',
    ];

    return Column(
      children: [
        for (final feature in features)
          ListTile(
            leading: const Icon(Icons.auto_awesome),
            title: Text(feature),
          ),
      ],
    );
  }
}
