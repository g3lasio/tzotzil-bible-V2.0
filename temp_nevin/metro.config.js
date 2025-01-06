const { getDefaultConfig } = require('@expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

module.exports = {
  ...config,
  resolver: {
    ...config.resolver,
    assetExts: [...config.resolver.assetExts, 'db', 'sqlite'],
    sourceExts: [...config.resolver.sourceExts, 'jsx', 'js', 'ts', 'tsx'],
    platforms: ['ios', 'android', 'web']
  },
  server: {
    port: 8083
  },
  transformer: {
    ...config.transformer,
    assetPlugins: ['expo-asset/tools/hashAssetFiles']
  }
};