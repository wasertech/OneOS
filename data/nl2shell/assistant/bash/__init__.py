from nl2shell.assistant.bash.en2shell import get_nl2shell_english_examples
# from nl2shell.assistant.bash.fr2shell import get_nl2shell_french_examples
from nl2shell.assistant.bash.date import get_date_examples
from nl2shell.assistant.bash.cd import get_cd_examples
from nl2shell.assistant.bash.ls import get_ls_data
from nl2shell.assistant.bash.pwd import get_pwd_data
from nl2shell.assistant.bash.cat import get_cat_examples
# from nl2shell.assistant.bash.rm import get_rm_examples
from nl2shell.assistant.bash.mv import get_mv_examples
from nl2shell.assistant.bash.cp import get_cp_examples
# from nl2shell.assistant.bash.grep import get_grep_examples
# from nl2shell.assistant.bash.find import get_find_examples
# from nl2shell.assistant.bash.sed import get_sed_examples
# from nl2shell.assistant.bash.awk import get_awk_examples
# from nl2shell.assistant.bash.head import get_head_examples
# from nl2shell.assistant.bash.tail import get_tail_examples
# from nl2shell.assistant.bash.sort import get_sort_examples
# from nl2shell.assistant.bash.uniq import get_uniq_examples
# from nl2shell.assistant.bash.wc import get_wc_examples
# from nl2shell.assistant.bash.cut import get_cut_examples
# from nl2shell.assistant.bash.tr import get_tr_examples
# from nl2shell.assistant.bash.split import get_split_examples
# from nl2shell.assistant.bash.join import get_join_examples
# from nl2shell.assistant.bash.touch import get_touch_examples
from nl2shell.assistant.bash.mkdir import get_mkdir_examples
from nl2shell.assistant.bash.md import get_md_examples
# from nl2shell.assistant.bash.rmdir import get_rmdir_examples
# from nl2shell.assistant.bash.chmod import get_chmod_examples
# from nl2shell.assistant.bash.chown import get_chown_examples
# from nl2shell.assistant.bash.chgrp import get_chgrp_examples
# from nl2shell.assistant.bash.useradd import get_useradd_examples
# from nl2shell.assistant.bash.userdel import get_userdel_examples
# from nl2shell.assistant.bash.usermod import get_usermod_examples
# from nl2shell.assistant.bash.groupadd import get_groupadd_examples
# from nl2shell.assistant.bash.groupdel import get_groupdel_examples
# from nl2shell.assistant.bash.groupmod import get_groupmod_examples
# from nl2shell.assistant.bash.passwd import get_passwd_examples
# from nl2shell.assistant.bash.sudo import get_sudo_examples
# from nl2shell.assistant.bash.su import get_su_examples
# from nl2shell.assistant.bash.ps import get_ps_examples
# from nl2shell.assistant.bash.kill import get_kill_examples
# from nl2shell.assistant.bash.pkill import get_pkill_examples
# from nl2shell.assistant.bash.pstree import get_pstree_examples
# from nl2shell.assistant.bash.top import get_top_examples
# from nl2shell.assistant.bash.free import get_free_examples
# from nl2shell.assistant.bash.df import get_df_examples
# from nl2shell.assistant.bash.mount import get_mount_examples
# from nl2shell.assistant.bash.umount import get_umount_examples
# from nl2shell.assistant.bash.iostat import get_iostat_examples
# from nl2shell.assistant.bash.vmstat import get_vmstat_examples
# from nl2shell.assistant.bash.netstat import get_netstat_examples
# from nl2shell.assistant.bash.ss import get_ss_examples
# from nl2shell.assistant.bash.lsof import get_lsof_examples
# from nl2shell.assistant.bash.w import get_w_examples
# from nl2shell.assistant.bash.who import get_who_examples
# from nl2shell.assistant.bash.last import get_last_examples
# from nl2shell.assistant.bash.lastlog import get_lastlog_examples
# from nl2shell.assistant.bash.lastb import get_lastb_examples
# from nl2shell.assistant.bash.history import get_history_examples
# from nl2shell.assistant.bash.alias import get_alias_examples
# from nl2shell.assistant.bash.unalias import get_unalias_examples
# from nl2shell.assistant.bash.which import get_which_examples
# from nl2shell.assistant.bash.ssh import get_ssh_examples
# from nl2shell.assistant.bash.chsh import get_chsh_examples
from nl2shell.assistant.bash.git import get_git_examples
from nl2shell.assistant.bash.docker import get_docker_examples


def get_bash_examples(langs=['en_US', 'fr_FR']):
    data = []

    data.extend(get_nl2shell_english_examples())
    # data.extend(get_nl2shell_french_examples())
    data.extend(get_date_examples())
    data.extend(get_cd_examples())
    data.extend(get_ls_data())
    data.extend(get_pwd_data())
    data.extend(get_cat_examples())
    data.extend(get_mkdir_examples())
    data.extend(get_md_examples())
    data.extend(get_cp_examples())
    data.extend(get_mv_examples())
    data.extend(get_git_examples())
    data.extend(get_docker_examples())

    return data


if __name__ == "__main__":
    data = get_bash_examples()
    for d in data:
        assert d.get('system', None) is not None, "System prompt is missing"
        assert d.get('instruction', None) is not None, "Instruction prompt is missing"
        assert d.get('conversation', None) is not None, "Conversation is missing"
        print()
        print(d)
        print()