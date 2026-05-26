import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/api_client.dart';
import 'core/auth_store.dart';
import 'core/theme.dart';
import 'screens/app_shell.dart';
import 'screens/login_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final api = ApiClient();
  final auth = AuthStore(api);
  await auth.restore();
  runApp(TonemindApp(api: api, auth: auth));
}

class TonemindApp extends StatelessWidget {
  const TonemindApp({super.key, required this.api, required this.auth});

  final ApiClient api;
  final AuthStore auth;

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider.value(value: api),
        ChangeNotifierProvider.value(value: auth),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'TONEMIND AI',
        theme: buildTonemindTheme(),
        home: Consumer<AuthStore>(
          builder: (context, store, _) => store.isAuthenticated ? const AppShell() : const LoginScreen(),
        ),
      ),
    );
  }
}
