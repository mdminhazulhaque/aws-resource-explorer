import { loadSharedConfigFiles } from "@smithy/shared-ini-file-loader";

export interface ProfileFilePaths {
  configFilepath?: string;
  filepath?: string;
}

export async function listProfiles(
  paths: ProfileFilePaths = {},
): Promise<string[]> {
  const { configFile, credentialsFile } = await loadSharedConfigFiles({
    ...paths,
    ignoreCache: true,
  });
  const names = new Set([
    ...Object.keys(configFile),
    ...Object.keys(credentialsFile),
  ]);
  return [...names].sort();
}
