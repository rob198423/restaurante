class AnalysisResult {
  const AnalysisResult({
    required this.id,
    required this.filename,
    required this.detectedKey,
    required this.bpm,
    required this.compatibleScales,
    required this.chords,
    required this.tablature,
  });

  final int id;
  final String filename;
  final String detectedKey;
  final double bpm;
  final List<String> compatibleScales;
  final List<String> chords;
  final List<TabNote> tablature;

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      id: json['id'] as int,
      filename: json['filename'] as String,
      detectedKey: json['detected_key'] as String,
      bpm: (json['bpm'] as num).toDouble(),
      compatibleScales: List<String>.from(json['compatible_scales'] as List),
      chords: List<String>.from(json['chords'] as List),
      tablature: (json['tablature'] as List)
          .map((item) => TabNote.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class TabNote {
  const TabNote({
    required this.timeSeconds,
    required this.stringNumber,
    required this.fret,
    required this.note,
  });

  final double timeSeconds;
  final int stringNumber;
  final int fret;
  final String note;

  factory TabNote.fromJson(Map<String, dynamic> json) {
    return TabNote(
      timeSeconds: (json['time_seconds'] as num).toDouble(),
      stringNumber: json['string'] as int,
      fret: json['fret'] as int,
      note: json['note'] as String,
    );
  }
}
