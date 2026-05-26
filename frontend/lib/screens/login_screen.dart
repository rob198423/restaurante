import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/auth_store.dart';
import '../core/theme.dart';
import '../widgets/glass_card.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final email = TextEditingController(text: 'demo@tonemind.ai');
  final name = TextEditingController(text: 'ToneMind Artist');
  final password = TextEditingController(text: 'tonemind123');
  bool register = false;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthStore>();
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(colors: [toneBg, Color(0xFF111A32), toneBg], begin: Alignment.topLeft, end: Alignment.bottomRight),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: GlassCard(
                child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  const Icon(Icons.graphic_eq_rounded, size: 64, color: toneCyan),
                  const SizedBox(height: 12),
                  Text('TONEMIND AI', textAlign: TextAlign.center, style: Theme.of(context).textTheme.displaySmall?.copyWith(fontWeight: FontWeight.w900)),
                  Text('AI music analysis studio', textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white60)),
                  const SizedBox(height: 28),
                  if (register) TextField(controller: name, decoration: const InputDecoration(labelText: 'Full name')),
                  if (register) const SizedBox(height: 12),
                  TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email')),
                  const SizedBox(height: 12),
                  TextField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Password')),
                  const SizedBox(height: 18),
                  if (auth.error != null) Text(auth.error!, style: const TextStyle(color: Colors.redAccent)),
                  ElevatedButton.icon(
                    onPressed: auth.busy ? null : () => register ? auth.register(email.text, name.text, password.text) : auth.login(email.text, password.text),
                    icon: auth.busy ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2)) : Icon(register ? Icons.person_add_alt : Icons.login),
                    label: Text(register ? 'Create account' : 'Login'),
                  ),
                  TextButton(onPressed: () => setState(() => register = !register), child: Text(register ? 'Already have an account' : 'Create a new account')),
                ]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
