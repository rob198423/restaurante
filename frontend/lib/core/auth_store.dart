import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';

class AuthStore extends ChangeNotifier {
  AuthStore(this.api);

  final ApiClient api;
  UserProfile? user;
  bool busy = false;
  String? error;

  bool get isAuthenticated => api.token != null;

  Future<void> restore() async {
    final prefs = await SharedPreferences.getInstance();
    api.token = prefs.getString('token');
    final email = prefs.getString('email');
    final name = prefs.getString('name');
    final id = prefs.getString('id');
    if (email != null && name != null && id != null) {
      user = UserProfile(id: id, email: email, fullName: name);
    }
    notifyListeners();
  }

  Future<void> login(String email, String password) => _run(() => api.login(email, password));

  Future<void> register(String email, String fullName, String password) => _run(() => api.register(email, fullName, password));

  Future<void> _run(Future<AuthPayload> Function() action) async {
    busy = true;
    error = null;
    notifyListeners();
    try {
      final payload = await action();
      user = payload.user;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', payload.token);
      await prefs.setString('id', payload.user.id);
      await prefs.setString('email', payload.user.email);
      await prefs.setString('name', payload.user.fullName);
    } catch (err) {
      error = err.toString();
    } finally {
      busy = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    api.token = null;
    user = null;
    notifyListeners();
  }
}
