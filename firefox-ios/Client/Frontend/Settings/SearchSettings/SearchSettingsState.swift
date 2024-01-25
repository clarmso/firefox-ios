// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/

import Redux

struct SearchSettingsState: ScreenState, Equatable {
    let windowUUID: WindowUUID

    init(_ appState: AppState, windowUUID: WindowUUID) {
        self.windowUUID = windowUUID
    }

    static let reducer: Reducer<Self> = { state, action in
        return state
    }
}
