import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Share,
  Platform,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../../App';
import * as Speech from 'expo-speech';

type QueryRoute = RouteProp<RootStackParamList, 'Query'>;

export default function QueryScreen() {
  const route = useRoute<QueryRoute>();
  const navigation = useNavigation();
  const { response, iterationCount, feedbackLog } = route.params;

  const sections = response.split('\n').reduce(
    (acc: { label: string; content: string[] }[], line: string) => {
      if (line.startsWith('---')) {
        acc.push({ label: line.replace(/---/g, '').trim(), content: [] });
      } else if (acc.length > 0) {
        acc[acc.length - 1].content.push(line);
      }
      return acc;
    },
    []
  );

  const handleShare = async () => {
    await Share.share({ message: response, title: 'Arth-Sutradhar Analysis' });
  };

  const handleSpeak = () => {
    Speech.speak(response, { language: 'en' });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={handleSpeak}>
          <Text style={styles.actionText}>Listen</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={handleShare}>
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.meta}>
        <Text style={styles.metaText}>
          Iterations: {iterationCount} | Feedback: {feedbackLog.length} steps
        </Text>
      </View>

      {sections.map((section, i) => (
        <View key={i} style={styles.section}>
          {section.label !== '' && (
            <Text style={styles.sectionTitle}>{section.label}</Text>
          )}
          {section.content.map((line, j) => (
            <Text key={j} style={styles.line}>
              {line}
            </Text>
          ))}
        </View>
      ))}

      <View style={styles.feedbackSection}>
        <Text style={styles.sectionTitle}>Agent Reasoning Log</Text>
        {feedbackLog.map((log, i) => (
          <View key={i} style={styles.logEntry}>
            <Text style={styles.logNumber}>{i + 1}.</Text>
            <Text style={styles.logText}>{log}</Text>
          </View>
        ))}
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: 12,
    gap: 8,
  },
  actionBtn: {
    backgroundColor: '#1a73e8',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  actionText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  meta: { paddingHorizontal: 16, marginBottom: 8 },
  metaText: { fontSize: 12, color: '#666' },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1a73e8',
    marginBottom: 8,
  },
  line: { fontSize: 13, color: '#333', lineHeight: 20, marginBottom: 2 },
  feedbackSection: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
  },
  logEntry: { flexDirection: 'row', marginBottom: 6 },
  logNumber: { fontSize: 12, color: '#999', width: 24 },
  logText: { fontSize: 12, color: '#555', flex: 1 },
});
