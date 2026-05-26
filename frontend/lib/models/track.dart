class Track {
  const Track({
    required this.id,
    required this.title,
    required this.mediaType,
    required this.sourceFilename,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.errorMessage,
  });

  final String id;
  final String title;
  final String mediaType;
  final String sourceFilename;
  final String status;
  final String? errorMessage;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory Track.fromJson(Map<String, dynamic> json) => Track(
        id: json['id'] as String,
        title: json['title'] as String,
        mediaType: json['media_type'] as String,
        sourceFilename: json['source_filename'] as String,
        status: json['status'] as String,
        errorMessage: json['error_message'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
        updatedAt: DateTime.parse(json['updated_at'] as String),
      );
}
