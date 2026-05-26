import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../models/analysis.dart';
import '../models/track.dart';

class ApiClient {
  ApiClient({String? baseUrl}) : baseUrl = baseUrl ?? const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');

  final String baseUrl;
  String? token;

  Map<String, String> get _jsonHeaders => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<AuthPayload> register(String email, String fullName, String password) async {
    final response = await http.post(
      _uri('/api/auth/register'),
      headers: _jsonHeaders,
      body: jsonEncode({'email': email, 'full_name': fullName, 'password': password}),
    );
    return _auth(response);
  }

  Future<AuthPayload> login(String email, String password) async {
    final response = await http.post(
      _uri('/api/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );
    return _auth(response);
  }

  AuthPayload _auth(http.Response response) {
    final data = _decode(response);
    token = data['access_token'] as String;
    return AuthPayload(token: token!, user: UserProfile.fromJson(data['user'] as Map<String, dynamic>));
  }

  Future<List<Track>> tracks() async {
    final response = await http.get(_uri('/api/tracks'), headers: _jsonHeaders);
    final data = _decode(response) as List<dynamic>;
    return data.map((item) => Track.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<Track> uploadTrack({required String title, required File file}) async {
    final request = http.MultipartRequest('POST', _uri('/api/tracks?title=${Uri.encodeQueryComponent(title)}'));
    if (token != null) request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return Track.fromJson(_decode(response) as Map<String, dynamic>);
  }

  Future<AnalysisResult> analyze(String trackId) async {
    final response = await http.post(_uri('/api/tracks/$trackId/analyze'), headers: _jsonHeaders);
    return AnalysisResult.fromJson(_decode(response) as Map<String, dynamic>);
  }

  Future<AnalysisResult> analysis(String trackId) async {
    final response = await http.get(_uri('/api/tracks/$trackId/analysis'), headers: _jsonHeaders);
    return AnalysisResult.fromJson(_decode(response) as Map<String, dynamic>);
  }

  Future<AnalysisResult> separate(String trackId) async {
    final response = await http.post(_uri('/api/analysis/$trackId/separate'), headers: _jsonHeaders);
    return AnalysisResult.fromJson(_decode(response) as Map<String, dynamic>);
  }

  Future<Uint8List> exportTrack(String trackId, String format) async {
    final response = await http.post(_uri('/api/exports/$trackId'), headers: _jsonHeaders, body: jsonEncode({'format': format}));
    if (response.statusCode >= 400) _throw(response);
    return response.bodyBytes;
  }

  Future<Map<String, dynamic>> tuner(double frequency) async {
    final response = await http.post(_uri('/api/tools/tuner'), headers: _jsonHeaders, body: jsonEncode({'frequency_hz': frequency}));
    return _decode(response) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> metronome(int bpm, int bars, int beatsPerBar) async {
    final response = await http.post(
      _uri('/api/tools/metronome'),
      headers: _jsonHeaders,
      body: jsonEncode({'bpm': bpm, 'bars': bars, 'beats_per_bar': beatsPerBar}),
    );
    return _decode(response) as Map<String, dynamic>;
  }

  dynamic _decode(http.Response response) {
    if (response.statusCode >= 400) _throw(response);
    if (response.body.isEmpty) return {};
    return jsonDecode(response.body);
  }

  Never _throw(http.Response response) {
    var detail = 'Request failed with status ${response.statusCode}';
    try {
      final body = jsonDecode(response.body);
      detail = body['detail']?.toString() ?? detail;
    } catch (_) {}
    throw ApiException(detail);
  }
}

class ApiException implements Exception {
  ApiException(this.message);
  final String message;
  @override
  String toString() => message;
}

class UserProfile {
  const UserProfile({required this.id, required this.email, required this.fullName});
  final String id;
  final String email;
  final String fullName;

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        id: json['id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
      );
}

class AuthPayload {
  const AuthPayload({required this.token, required this.user});
  final String token;
  final UserProfile user;
}
