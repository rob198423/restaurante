import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/analysis_result.dart';

class ApiClient {
  ApiClient({required this.baseUrl});

  final String baseUrl;
  String? _token;

  Future<void> login({required String email, required String password}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 401 || response.statusCode == 404) {
      await register(email: email, password: password);
      return login(email: email, password: password);
    }

    _throwForError(response);
    _token = jsonDecode(response.body)['access_token'] as String;
  }

  Future<void> register({required String email, required String password}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (response.statusCode != 409) {
      _throwForError(response);
    }
  }

  Future<AnalysisResult> uploadAudio(File file) async {
    final token = _token;
    if (token == null) {
      throw StateError('Login required before uploading audio.');
    }

    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/audio/upload'));
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    _throwForError(response);
    return AnalysisResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  void _throwForError(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return;
    }
    throw HttpException('API error ${response.statusCode}: ${response.body}');
  }
}
