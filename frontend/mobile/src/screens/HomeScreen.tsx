import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { sendQuery, uploadImage, healthCheck } from '../services/api';
import { RootStackParamList } from '../../App';

type HomeNav = NativeStackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<HomeNav>();
  const [queryText, setQueryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [serverOnline, setServerOnline] = useState(false);

  useEffect(() => {
    healthCheck()
      .then(() => setServerOnline(true))
      .catch(() => setServerOnline(false));
  }, []);

  const handleTextQuery = useCallback(async () => {
    if (!queryText.trim()) {
      Alert.alert('Input Required', 'Please enter a query.');
      return;
    }
    setLoading(true);
    try {
      const result = await sendQuery(queryText.trim());
      navigation.navigate('Query', {
        response: result.response,
        iterationCount: result.iteration_count,
        feedbackLog: result.feedback_log,
      });
    } catch (err: any) {
      Alert.alert('Error', err.message);
    } finally {
      setLoading(false);
    }
  }, [queryText, navigation]);

  const handleVoiceInput = useCallback(async () => {
    try {
      const Voice = require('@react-native-voice/voice').default;
      Voice.start('gu-IN');
      Voice.onSpeechResults = (e: any) => {
        if (e.value?.length) {
          setQueryText(e.value[0]);
        }
      };
    } catch {
      Alert.alert('Voice', 'Voice input not available on this device.');
    }
  }, []);

  const handleImageUpload = useCallback(async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission Needed', 'Camera access is required.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
    });
    if (result.canceled || !result.assets?.length) return;

    setLoading(true);
    try {
      const apiResult = await uploadImage(result.assets[0].uri);
      navigation.navigate('Query', {
        response: apiResult.response,
        iterationCount: apiResult.iteration_count,
        feedbackLog: apiResult.feedback_log,
      });
    } catch (err: any) {
      Alert.alert('Upload Error', err.message);
    } finally {
      setLoading(false);
    }
  }, [navigation]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Arth-Sutradhar</Text>
        <Text style={styles.subtitle}>The Economic Narrator</Text>
        <View
          style={[
            styles.statusDot,
            { backgroundColor: serverOnline ? '#34a853' : '#ea4335' },
          ]}
        />
        <Text style={styles.statusText}>
          {serverOnline ? 'API connected' : 'API offline'}
        </Text>
      </View>

      <View style={styles.inputSection}>
        <TextInput
          style={styles.textInput}
          placeholder="Ask about land records, inflation, crops..."
          placeholderTextColor="#999"
          value={queryText}
          onChangeText={setQueryText}
          multiline
          numberOfLines={4}
        />

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, styles.textButton]}
            onPress={handleTextQuery}
            disabled={loading}
          >
            <Text style={styles.buttonText}>Ask</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.voiceButton]}
            onPress={handleVoiceInput}
          >
            <Text style={styles.buttonText}>Voice</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.imageButton]}
            onPress={handleImageUpload}
            disabled={loading}
          >
            <Text style={styles.buttonText}>Camera</Text>
          </TouchableOpacity>
        </View>
      </View>

      {loading && (
        <View style={styles.loading}>
          <ActivityIndicator size="large" color="#1a73e8" />
          <Text style={styles.loadingText}>Agent is analyzing...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 20,
    backgroundColor: '#1a73e8',
  },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff' },
  subtitle: { fontSize: 14, color: '#e8e8e8', marginTop: 4 },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginTop: 12,
  },
  statusText: { fontSize: 12, color: '#e8e8e8', marginTop: 4 },
  inputSection: { padding: 20 },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    backgroundColor: '#fff',
    minHeight: 100,
    textAlignVertical: 'top',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  textButton: { backgroundColor: '#1a73e8' },
  voiceButton: { backgroundColor: '#34a853' },
  imageButton: { backgroundColor: '#ea4335' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  loading: { alignItems: 'center', marginTop: 30 },
  loadingText: { marginTop: 10, fontSize: 14, color: '#666' },
});
