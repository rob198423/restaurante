import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

const toneBg = Color(0xFF080A12);
const tonePanel = Color(0xFF101522);
const tonePanelSoft = Color(0xFF182033);
const toneAccent = Color(0xFF7C4DFF);
const toneCyan = Color(0xFF00E5FF);
const toneGreen = Color(0xFF38E28A);
const toneText = Color(0xFFF5F7FB);

ThemeData buildTonemindTheme() {
  final base = ThemeData.dark(useMaterial3: true);
  final textTheme = GoogleFonts.interTextTheme(base.textTheme).apply(bodyColor: toneText, displayColor: toneText);
  return base.copyWith(
    scaffoldBackgroundColor: toneBg,
    colorScheme: const ColorScheme.dark(
      primary: toneAccent,
      secondary: toneCyan,
      tertiary: toneGreen,
      surface: tonePanel,
      onSurface: toneText,
    ),
    textTheme: textTheme,
    appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0, centerTitle: false),
    cardTheme: CardTheme(color: tonePanel, elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: tonePanelSoft,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(18), borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(18), borderSide: const BorderSide(color: toneCyan)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: toneAccent,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
    ),
  );
}
