import 'package:flutter/material.dart';

import 'core/api_client.dart';
import 'core/app_theme.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const ToneMindApp());
}

class ToneMindApp extends StatelessWidget {
  const ToneMindApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient(
      baseUrl: const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://10.0.2.2:8000',
      ),
    );

    return MaterialApp(
      title: 'ToneMind AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark(),
      home: LoginScreen(apiClient: apiClient),
    );
  }
}
