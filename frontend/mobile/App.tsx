import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from './src/screens/HomeScreen';
import QueryScreen from './src/screens/QueryScreen';
import { AppScreen } from './src/types';

export type RootStackParamList = {
  Home: undefined;
  Query: { response: string; iterationCount: number; feedbackLog: string[] };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: '#1a73e8' },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: 'bold' },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Arth-Sutradhar' }}
        />
        <Stack.Screen
          name="Query"
          component={QueryScreen}
          options={{ title: 'Analysis Result' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
