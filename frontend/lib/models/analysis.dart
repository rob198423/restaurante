import 'track.dart';

class AnalysisResult {
  const AnalysisResult({required this.track, required this.summary, required this.chords, required this.scales, required this.modes, required this.tablature, required this.stems});

  final Track track;
  final Map<String, dynamic> summary;
  final List<Map<String, dynamic>> chords;
  final List<Map<String, dynamic>> scales;
  final List<Map<String, dynamic>> modes;
  final Map<String, dynamic> tablature;
  final Map<String, dynamic> stems;

  factory AnalysisResult.fromJson(Map<String, dynamic> json) => AnalysisResult(
        track: Track.fromJson(json['track'] as Map<String, dynamic>),
        summary: Map<String, dynamic>.from(json['summary'] as Map),
        chords: (json['chords'] as List<dynamic>).map((item) => Map<String, dynamic>.from(item as Map)).toList(),
        scales: (json['scales'] as List<dynamic>).map((item) => Map<String, dynamic>.from(item as Map)).toList(),
        modes: (json['modes'] as List<dynamic>).map((item) => Map<String, dynamic>.from(item as Map)).toList(),
        tablature: Map<String, dynamic>.from(json['tablature'] as Map),
        stems: Map<String, dynamic>.from(json['stems'] as Map),
      );
}
