clear all; close all; clc;

%% part 1 - merge game data files
total_games = 10+ 21+ 20;

no_of_data_parameters = 107;

all_data = zeros(0, no_of_data_parameters + 2);

labels = zeros(0,1);

players_ids = [1*ones(10, 1); 2*ones(21,1); 3*ones(20,1)];
game_ids = [ [0:9]'; [0:20]'; [0:19]' ];

% Get game data
for game = 1:total_games
    players_id = players_ids(game);
    game_id = game_ids(game);

    % get game file and read table
    data_filename = sprintf('..//dataset_%d_game_%02d_distances_in_radius_data.csv', players_id, game_id);
    game_data_table = readtable(data_filename);

    % get labels file and read table
    labels_filename = sprintf(['vf_label_dataset_%d_game_%02d.csv'], players_id, game_id);
    labels_data_table = readtable(labels_filename);

    % convert table and labels to array
    game_data_array = table2array(game_data_table);
    labels_data_array = table2array(labels_data_table);

    % add players_id and game_id to array
    players_id_vector = players_id*ones(height(game_data_array),1);
    game_id_vector = game_id*ones(height(game_data_array), 1);

    big_game_data_array = [players_id_vector, game_id_vector, game_data_array];

    % append array to all_data and labels
    all_data = [all_data; big_game_data_array];

    labels = [labels; labels_data_array];
end

% Make Table and Save File
new_variable_names = horzcat( {'players_id', 'game_id'}, game_data_table.Properties.VariableNames);

all_data_table = array2table(all_data, 'VariableNames', new_variable_names);
save_file_name = sprintf("allgames_data.csv");
writetable(all_data_table, save_file_name)

labels_table = array2table(labels,'VariableNames',{'value_function_label'});
labels_file_name = sprintf("allgames_labels.csv");
writetable(labels_table, labels_file_name)