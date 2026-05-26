import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/auth_store.dart';
import '../core/theme.dart';
import 'analysis_screen.dart';
import 'history_screen.dart';
import 'home_screen.dart';
import 'tools_screen.dart';
import 'upload_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int index = 0;
  final screens = const [HomeScreen(), UploadScreen(), AnalysisScreen(), ToolsScreen(), HistoryScreen()];

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.of(context).size.width > 760;
    final auth = context.watch<AuthStore>();
    final navItems = const [
      NavigationDestination(icon: Icon(Icons.dashboard_rounded), label: 'Studio'),
      NavigationDestination(icon: Icon(Icons.cloud_upload_rounded), label: 'Upload'),
      NavigationDestination(icon: Icon(Icons.auto_graph_rounded), label: 'Analysis'),
      NavigationDestination(icon: Icon(Icons.tune_rounded), label: 'Tools'),
      NavigationDestination(icon: Icon(Icons.history_rounded), label: 'History'),
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text('TONEMIND AI'),
        actions: [
          Center(child: Text(auth.user?.fullName ?? '', style: const TextStyle(color: Colors.white70))),
          IconButton(onPressed: auth.logout, icon: const Icon(Icons.logout_rounded)),
        ],
      ),
      body: Row(
        children: [
          if (wide)
            NavigationRail(
              backgroundColor: tonePanel,
              selectedIndex: index,
              onDestinationSelected: (value) => setState(() => index = value),
              labelType: NavigationRailLabelType.all,
              destinations: navItems.map((item) => NavigationRailDestination(icon: item.icon, label: Text(item.label))).toList(),
            ),
          Expanded(child: screens[index]),
        ],
      ),
      bottomNavigationBar: wide ? null : NavigationBar(selectedIndex: index, onDestinationSelected: (value) => setState(() => index = value), destinations: navItems),
    );
  }
}
